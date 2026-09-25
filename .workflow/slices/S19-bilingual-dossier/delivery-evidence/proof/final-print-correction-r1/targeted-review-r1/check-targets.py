from pathlib import Path
import json
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
 reports.append(report)
result={'documents':len(reports),'pages':sum(len(r['pages']) for r in reports),'issues':[{'pdf':r['pdf'],'issues':r['issues']} for r in reports if r['issues']],'reports':reports}
Path('/proof/TARGET-STRICT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='reports'}));assert len(reports)==4 and not result['issues']
