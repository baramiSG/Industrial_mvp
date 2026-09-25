from __future__ import annotations
import argparse,hashlib,json,platform
from pathlib import Path
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
reports=[]
for path in sorted(args.input.glob('*.pdf')):
 doc=pdfium.PdfDocument(path);reader=PdfReader(path);pages=[]
 for i in range(len(doc)):
  page=doc[i];w,h=page.get_size();text=page.get_textpage();raw=text.get_text_range();bad=[];boxes=[]
  for n in range(text.count_chars()):
   box=tuple(float(v) for v in text.get_charbox(n,loose=False));l,b,r,t=box
   if r>l and t>b:
    boxes.append(box)
    if l < -0.01 or b < -0.01 or r > w+0.01 or t > h+0.01:bad.append({'index':n,'box':box})
  png=args.output/f'{path.stem}-page-{i+1:02}.png';bitmap=page.render(scale=2,rotation=0,crop=(0,0,0,0));pil=bitmap.to_pil();pil.save(png)
  textfile=png.with_suffix('.txt');textfile.write_text(raw)
  pages.append({'page':i+1,'size_pt':[w,h],'raster_px':list(pil.size),'png':png.name,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'chars':text.count_chars(),'nonzero_character_boxes':len(boxes),'page_bounds_violations':bad,'text_sha256':hashlib.sha256(textfile.read_bytes()).hexdigest()})
  pil.close();bitmap.close();text.close();page.close()
 reports.append({'pdf':path.name,'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'metadata':{str(k):str(v) for k,v in reader.metadata.items()},'pages':pages});doc.close()
result={'pypdfium2':str(pdfium.PYPDFIUM_INFO),'pdfium':str(pdfium.PDFIUM_INFO),'python':platform.python_version(),'pillow':Image.__version__,'scale':2,'dpi':144,'page_bound_tolerance_pt':0.01,'bounds_method':'Tight nonzero glyph boxes against whole PDF page; does not prove declared content-region or overlap safety','reports':reports}
(args.output/'RENDER-RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'documents':len(reports),'pages':sum(len(r['pages']) for r in reports),'page_bounds_violations':sum(len(p['page_bounds_violations']) for r in reports for p in r['pages']),'pypdfium2':result['pypdfium2'],'pdfium':result['pdfium']}))
