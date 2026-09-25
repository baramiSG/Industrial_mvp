from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from browser_tests.harness import start_app_server,stop_app_server,ROOT
from browser_tests.visual_baselines import LAUNCH_FLAGS
server=start_app_server(ROOT,Path('/proof/server'))
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(args=list(LAUNCH_FLAGS))
  page=browser.new_page(viewport={'width':1440,'height':900})
  response=page.goto(server.base_url+'/api/opportunities/SAU-H0-390210/dossier.html?mode=simulated&locale=ar')
  assert response.status==200
  page.evaluate('document.fonts.ready');page.emulate_media(media='print')
  result=page.evaluate("""() => {
    const term=[...document.querySelectorAll('.record-group > dt')].find(e=>e.textContent==='الكمية');
    if(!term) throw new Error('Actual quantity record missing');
    const group=term.parentElement,dd=term.nextElementSibling,dl=dd.firstElementChild,row=dl.firstElementChild;
    const elements={group,term,dd,dl,row,firstTerm:row.firstElementChild,firstValue:row.lastElementChild};
    return {html:group.outerHTML,computed:Object.fromEntries(Object.entries(elements).map(([name,e])=>{
      const s=getComputedStyle(e);return [name,{tag:e.tagName,class:e.className,text:e.textContent,display:s.display,breakBefore:s.breakBefore,breakAfter:s.breakAfter,breakInside:s.breakInside,marginTop:s.marginTop,marginBottom:s.marginBottom,paddingTop:s.paddingTop,paddingBottom:s.paddingBottom}];}))};
  }""")
  Path('/proof/COMPUTED-DOM.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  print(json.dumps({'status':'OBSERVED_UNCHANGED_SOURCE','elements':len(result['computed']),'termBreakAfter':result['computed']['term']['breakAfter'],'firstValue':result['computed']['firstValue']['text']}))
  browser.close()
finally:stop_app_server(server)
