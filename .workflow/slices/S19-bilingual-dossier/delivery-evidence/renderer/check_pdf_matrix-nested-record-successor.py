"""Finite S19 44-document acceptance; complements unchanged PDFium rasterizer."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, re, unicodedata
import pypdfium2 as pdfium
from pypdf import PdfReader
from browser_tests.harness import CASES
from ior_mvp.config import ui_strings_bundle
from ior_mvp.evidence import synthetic_display_labels
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import build_dossier

MM=72/25.4
MARGIN=14*MM
FOOTER=27*MM
TOLERANCE=0.01
SECTIONS=('identity','demand','supply','gap','capability','economics','competition','ledger','evidence','conditions','authority')
LABELS=synthetic_display_labels()

def normalized(value):
    return ''.join(char for char in unicodedata.normalize('NFKC',value) if not char.isspace() and unicodedata.category(char)!='Cf' and char!='\x00')

def arabic_chars(value):
    return Counter(char for char in unicodedata.normalize('NFKC',value) if '\u0600'<=char<='\u06ff')

def label_present(text,label,locale):
    if locale=='en':return normalized(label) in normalized(text)
    # PDF visual text order is supplementary evidence, not Arabic reading-order proof.
    expected=Counter(normalized(label));lines=text.splitlines()
    return any(Counter(normalized(''.join(lines[start:start+length])))==expected for start in range(len(lines)) for length in (1,2,3))

def font_records(page):
    records=[]
    for name,ref in page.get('/Resources',{}).get('/Font',{}).items():
        font=ref.get_object();descendants=font.get('/DescendantFonts',[])
        descriptors=[font.get('/FontDescriptor')]+[child.get_object().get('/FontDescriptor') for child in descendants]
        embedded=any(item and any(key in item.get_object() for key in ('/FontFile','/FontFile2','/FontFile3')) for item in descriptors)
        glyphs=font.get('/CharProcs',{})
        type3_embedded=font.get('/Subtype')=='/Type3' and bool(glyphs) and all(bool(ref.get_object().get_data()) for ref in glyphs.values())
        descriptor=font.get('/FontDescriptor')
        font_name=font.get('/BaseFont') or (descriptor.get_object().get('/FontName','') if descriptor else '')
        unicode_map=font.get('/ToUnicode')
        records.append({'resource':str(name),'name':str(font_name),'subtype':str(font.get('/Subtype')),'embedded':bool(embedded or type3_embedded),'type3_glyph_programs':len(glyphs),'unicode_map':bool(unicode_map and unicode_map.get_object().get_data())})
    return records

def inspect_pdf(path,mode,locale):
    doc=pdfium.PdfDocument(path);reader=PdfReader(path);issues=[];pages=[];texts=[]
    if not path.read_bytes().startswith(b'%PDF-') or not path.read_bytes().rstrip().endswith(b'%%EOF'):issues.append('invalid PDF structure')
    if len(doc)!=len(reader.pages) or len(doc)<2:issues.append('invalid or missing page count')
    for index in range(len(doc)):
        page=doc[index];width,height=page.get_size();text=page.get_textpage();raw=text.get_text_range();texts.append(raw)
        prefix=f'page{index+1}'
        if abs(width-210*MM)>1 or abs(height-297*MM)>1:issues.append(prefix+': non-A4')
        footer=text.get_text_bounded(left=0,bottom=0,right=width,top=FOOTER)
        body=text.get_text_bounded(left=MARGIN,bottom=FOOTER,right=width-MARGIN,top=height-MARGIN)
        if not normalized(body):issues.append(prefix+': no selectable body text')
        if '\ufffd' in raw:issues.append(prefix+': replacement character')
        physical=[];content=[];footer_boxes=[];body_boxes=[]
        for char_index in range(text.count_chars()):
            box=tuple(float(v) for v in text.get_charbox(char_index,loose=False));left,bottom,right,top=box
            if right<=left or top<=bottom:continue
            if left<-.01 or bottom<-.01 or right>width+.01 or top>height+.01:physical.append({'character':char_index,'box':box})
            if top<=FOOTER:
                footer_boxes.append(box)
                if mode=='public':content.append({'character':char_index,'box':box,'reason':'public content in footer'})
            else:
                body_boxes.append(box)
                if left<MARGIN-TOLERANCE or right>width-MARGIN+TOLERANCE or bottom<FOOTER-TOLERANCE or top>height-MARGIN+TOLERANCE:content.append({'character':char_index,'box':box,'reason':'outside declared content region'})
        if physical:issues.append(prefix+': physical glyph bounds')
        if content:issues.append(prefix+': content glyph bounds')
        if mode=='simulated':
            if footer.count(LABELS['en'])!=1 or arabic_chars(footer)!=arabic_chars(LABELS['ar']):issues.append(prefix+': footer policy missing/malformed/displaced')
            if not footer_boxes or not body_boxes or min(box[1] for box in body_boxes)<=max(box[3] for box in footer_boxes):issues.append(prefix+': no positive body/footer separation')
        elif LABELS['en'] in raw or arabic_chars(footer):issues.append(prefix+': synthetic policy in public PDF')
        fonts=font_records(reader.pages[index])
        if not fonts or any(not row['embedded'] or not row['unicode_map'] for row in fonts):issues.append(prefix+': missing embedded font/Unicode map')
        pages.append({'page':index+1,'chars':text.count_chars(),'physical_violations':physical,'content_violations':content,'footer_text':footer,'fonts':fonts,'body_footer_separation_pt':min((box[1] for box in body_boxes),default=0)-max((box[3] for box in footer_boxes),default=0) if footer_boxes else None})
        text.close();page.close()
    doc.close()
    return {'pdf':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':pages,'issues':issues},texts

def narrative_issues(texts,analysis,locale):
    narrative=analysis['real_decision']['localized_narrative'][locale]
    entries=[(key,narrative[key]['text']) for key in ('headline','rationale','route_label')]
    entries += [(key+':'+str(index),entry['text']) for key in ('conditions','kill_conditions','missing_facts') for index,entry in enumerate(narrative.get(key,[]))]
    whole='\n'.join(texts);compact=normalized(whole);lines=[normalized(line) for line in whole.splitlines() if normalized(line)]
    def present(value):
        expected=normalized(value)
        if expected in compact:return True
        if locale=='en':return False
        # Retain full character multiplicity in a contiguous visual-text window.
        # Exact Arabic reading order is separately inspected in actual rasters.
        counter=Counter(expected);size=len(expected)
        observed=Counter(compact[:size])
        if observed==counter:return True
        for index in range(size,len(compact)):
            outgoing=compact[index-size];observed[outgoing]-=1
            if observed[outgoing]==0:del observed[outgoing]
            observed[compact[index]]+=1
            if observed==counter:return True
        return False
    return ['missing complete public narrative:'+key for key,value in entries if not present(value)]

def raster_issues(rendered,pdf_root,expected):
    issues=[];record=rendered/'RENDER-RESULT.json'
    if not record.is_file():return ['missing renderer result']
    result=json.loads(record.read_text());reports=result['reports']
    if result['dpi']!=144 or result['scale']!=2:issues.append('wrong raster resolution')
    if {row['pdf'] for row in reports}!=set(expected) or len(reports)!=44:issues.append('missing/duplicate rendered document')
    required=set()
    for report in reports:
        path=pdf_root/report['pdf']
        if not path.is_file():issues.append('missing PDF:'+path.name);continue
        if report['pdf_sha256']!=hashlib.sha256(path.read_bytes()).hexdigest():issues.append('PDF/raster hash mismatch:'+path.name)
        summary=pdf_root/(path.stem+'-summary.json')
        if not summary.is_file():issues.append('missing produced page count:'+path.name);continue
        count=json.loads(summary.read_text())['page_objects']
        if len(PdfReader(path).pages)!=count or len(report['pages'])!=count or [row['page'] for row in report['pages']]!=list(range(1,count+1)):issues.append('missing/duplicate PDF or raster page:'+path.name)
        for page in report['pages']:
            png=rendered/page['png'];text=png.with_suffix('.txt');required.update((png.name,text.name))
            for asset,key in ((png,'png_sha256'),(text,'text_sha256')):
                if not asset.is_file():issues.append('missing rendered asset:'+asset.name)
                elif hashlib.sha256(asset.read_bytes()).hexdigest()!=page[key]:issues.append('rendered asset hash mismatch:'+asset.name)
            if page['page_bounds_violations']:issues.append('renderer physical glyph bounds:'+png.name)
    actual={path.name for path in rendered.iterdir() if path.suffix in ('.png','.txt')}
    if actual!=required:issues.append('rendered page asset inventory mismatch')
    return issues

def document_issues(pdf_root,expected):
    actual={p.name for p in pdf_root.glob('*.pdf')}
    return [] if actual==set(expected) else [{'matrix_missing':sorted(set(expected)-actual),'matrix_unexpected':sorted(actual-set(expected))}]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--rendered',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    expected={f'{case.slug}-{mode}-{locale}.pdf':(case,mode,locale) for case in CASES for mode in ('public','simulated') for locale in ('en','ar')}
    assert len(expected)==44
    actual={p.name for p in args.input.glob('*.pdf')};issues=[];reports=[]
    issues.extend(raster_issues(args.rendered,args.input,expected))
    issues.extend(document_issues(args.input,expected))
    for name,(case,mode,locale) in expected.items():
        path=args.input/name
        if not path.is_file():continue
        report,texts=inspect_pdf(path,mode,locale);whole='\n'.join(texts);compact=normalized(whole);strings=ui_strings_bundle(locale)['strings']
        analysis=analyze(case.id,mode);dossier=build_dossier(analysis)
        if dossier['public_decision']!=analysis['real_decision']:report['issues'].append('public decision changed')
        report['issues'].extend(narrative_issues(texts,analysis,locale))
        for section in SECTIONS:
            if not label_present(whole,strings['dossier.section.'+section],locale):report['issues'].append('missing section heading:'+section)
        if not label_present(texts[0],strings['dossier.summary'],locale):report['issues'].append('summary not page1')
        if label_present(texts[0],strings['dossier.contents'],locale) or not label_present(texts[1],strings['dossier.contents'],locale):report['issues'].append('appendix not page2')
        ids={case.id,analysis['snapshot_id'],*[row['evidence_id'] for row in dossier['evidence_pack']['passports']],*[row['evidence_id'] for row in dossier['evidence_pack']['external_dependencies']]}
        for value in sorted(ids):
            if normalized(value) not in compact:report['issues'].append('missing complete technical ID:'+value)
        for block in dossier['blocks'].values():
            for field in block['fields']:
                value=field['value']
                if field['availability']=='AVAILABLE' and isinstance(value,(int,float)) and not isinstance(value,bool):
                    if normalized(format(value,'.12g')) not in compact:report['issues'].append('missing source numeric value:'+field['key'])
                    if field['unit'] and normalized(field['unit']) not in compact:report['issues'].append('missing source numeric unit:'+field['key'])
        if mode=='public' and ('SYN-MINISTRY-' in compact or LABELS['en'] in whole):report['issues'].append('public synthetic payload')
        # Five reviewed orphan instances: exact source occurrence, order and page.
        if mode=='simulated' and locale=='ar' and case.slug in ('polypropylene','alu-profiles','penicillin-api'):
            lines=[(index+1,line) for index,text in enumerate(texts) for line in text.splitlines() if normalized(line)]
            specs=[]
            if case.slug=='polypropylene':
                rule=next(row for row in dossier['blocks']['ledger']['records']['rules'] if row['rule_id']=='R3')
                specs.append(('NESTED-DT-02','R3','R4-F',strings['dossier.field.quantity'],strings['dossier.field.basis']+rule['metrics']['quantity']['basis'],False))
            if case.slug=='alu-profiles':
                raw=dossier['evidence_pack']['scenario_inputs']['economics']
                specs.append(('NESTED-DT-04',None,'SYN-MINISTRY-ALU-PROFILES-001::economics',strings['dossier.field.national_value'],strings['dossier.field.displacement']+format(raw['data']['national_value']['displacement'],'.12g'),False))
            if case.slug in ('alu-profiles','penicillin-api'):
                rule=next(row for row in dossier['blocks']['ledger']['records']['rules'] if row['rule_id']=='R1-D')
                specs.append(('CAPTION-ORPHAN-02' if case.slug=='alu-profiles' else 'CAPTION-ORPHAN-01','R1-D','R2',strings['dossier.source_original'],strings['dossier.field.positive_years']+''.join(str(year) for year in rule['metrics']['positive_years']),True))
            report['record_associations']=[]
            for finding,start_token,end_token,heading,first_fact,bullets in specs:
                association={'finding':finding,'heading':heading,'complete_first_fact':first_fact,'start_token':start_token,'end_token':end_token,'heading_windows':[],'first_row_windows':[]}
                start=0;end=len(lines);boundary_ok=True
                if start_token:
                    starts=[index for index,(_,line) in enumerate(lines) if re.search(r'(?<![A-Za-z0-9-])'+re.escape(start_token)+r'(?![A-Za-z0-9-])',line)]
                    ends=[index for index,(_,line) in enumerate(lines) if re.search(r'(?<![A-Za-z0-9-])'+re.escape(end_token)+r'(?![A-Za-z0-9-])',line)]
                    boundary_ok=len(starts)==len(ends)==1 and starts[0]<ends[0]
                    if boundary_ok:start,end=starts[0]+1,ends[0]
                    association['boundary_starts']=starts;association['boundary_ends']=ends
                if boundary_ok:
                    for index in range(start,end):
                        for length in (1,2,3):
                            if index+length>end:continue
                            window=''.join(line for _,line in lines[index:index+length])
                            if len(normalized(window))==len(normalized(heading)) and label_present(window,heading,locale):
                                association['heading_windows'].append({'line':index,'length':length,'pages':sorted({page for page,_ in lines[index:index+length]}),'text':window});break
                heads=association['heading_windows']
                if boundary_ok and len(heads)==1:
                    head=heads[0];after=head['line']+head['length']
                    if start_token is None:
                        ends=[index for index in range(after,len(lines)) if normalized(end_token) in normalized(lines[index][1])]
                        boundary_ok=bool(ends)
                        if boundary_ok:end=ends[0]
                        association['following_source_boundary']=ends[0] if ends else None
                    if boundary_ok:
                        for index in range(after,end):
                            for length in (1,2,3):
                                if index+length>end:continue
                                window=''.join(line for _,line in lines[index:index+length])
                                if bullets:window=window.replace('•','')
                                if len(normalized(window))==len(normalized(first_fact)) and label_present(window,first_fact,locale):
                                    association['first_row_windows'].append({'line':index,'length':length,'pages':sorted({page for page,_ in lines[index:index+length]}),'text':window});break
                first=association['first_row_windows']
                association['passed']=bool(boundary_ok and len(heads)==len(first)==1 and len(heads[0]['pages'])==1 and heads[0]['pages']==first[0]['pages'])
                report['record_associations'].append(association)
                if not association['passed']:report['issues'].append('orphan/missing/ambiguous ordered first record:'+finding)
        if report['issues']:issues.append({'pdf':name,'issues':report['issues']})
        (args.output/(path.stem+'.txt')).write_text(whole)
        reports.append(report)
    result={'scope':'S19 actual44-document finite PDF acceptance, not raster/manual review or delivery approval','tolerance_pt':TOLERANCE,'declared_content_region_mm':{'top':14,'left':14,'right':14,'bottom':27},'arabic_note':'Visual-order character comparisons supplement exact HTML/CSS source tests and required manual raster review; they do not establish Arabic reading order.','documents':len(reports),'pages':sum(len(row['pages']) for row in reports),'issues':issues,'reports':reports}
    (args.output/'PDF-ACCEPTANCE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'documents':result['documents'],'pages':result['pages'],'failures':issues},ensure_ascii=False))
    raise SystemExit(bool(issues))
if __name__=='__main__':main()
