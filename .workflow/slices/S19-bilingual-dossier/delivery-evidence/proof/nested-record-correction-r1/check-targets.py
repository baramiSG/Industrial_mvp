from pathlib import Path
import json,re
from check_pdf_matrix import inspect_pdf,narrative_issues,normalized,label_present,SECTIONS,CASES,ui_strings_bundle,analyze,build_dossier,LABELS
root=Path('/proof/pdf');reports=[]
for path in sorted(root.glob('*.pdf')):
 name=path.stem;locale=name[-2:];mode='simulated' if '-simulated-' in name else 'public';slug=name.rsplit('-'+mode+'-',1)[0]
 case=next(case for case in CASES if case.slug==slug);analysis=analyze(case.id,mode);dossier=build_dossier(analysis)
 report,texts=inspect_pdf(path,mode,locale);report['issues']+=narrative_issues(texts,analysis,locale)
 strings=ui_strings_bundle(locale)['strings'];whole='\n'.join(texts);compact=normalized(whole)
 assert dossier['public_decision']==analysis['real_decision']
 for section in SECTIONS:
  if not label_present(whole,strings['dossier.section.'+section],locale):report['issues'].append('missing heading:'+section)
 if not label_present(texts[0],strings['dossier.summary'],locale):report['issues'].append('summary missing on first page')
 if label_present(texts[0],strings['dossier.contents'],locale) or not label_present(texts[1],strings['dossier.contents'],locale):report['issues'].append('appendix not page2')
 for value in {case.id,analysis['snapshot_id'],*[row['evidence_id'] for row in dossier['evidence_pack']['passports']],*[row['evidence_id'] for row in dossier['evidence_pack']['external_dependencies']]}:
  if normalized(value) not in compact:report['issues'].append('missing complete ID:'+value)
 for block in dossier['blocks'].values():
  for field in block['fields']:
   value=field['value']
   if field['availability']=='AVAILABLE' and isinstance(value,(int,float)) and not isinstance(value,bool):
    if normalized(format(value,'.12g')) not in compact:report['issues'].append('missing numeric:'+field['key'])
    if field['unit'] and normalized(field['unit']) not in compact:report['issues'].append('missing unit:'+field['key'])
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
 reports.append(report)
result={'documents':len(reports),'pages':sum(len(r['pages']) for r in reports),'issues':[{'pdf':r['pdf'],'issues':r['issues']} for r in reports if r['issues']],'reports':reports}
Path('/proof/TARGET-STRICT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='reports'}));assert len(reports)==4 and not result['issues']
