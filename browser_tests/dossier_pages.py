"""Dossier-only content and rendered-bounds checks using the stock harness."""
import json
from playwright.sync_api import expect
from browser_tests.pages import locale_bundle

MEASURE = """async selectors => {
  await document.fonts.ready;
  await new Promise(requestAnimationFrame);
  const items = {};
  for (const [name, selector] of Object.entries(selectors)) {
    const node = document.querySelector(selector);
    if (!node) { items[name] = {missing: true}; continue; }
    const r = node.getBoundingClientRect();
    const range = document.createRange(); range.selectNodeContents(node);
    const rects = [...range.getClientRects()].filter(r => r.width && r.height);
    items[name] = {text: node.textContent.trim(), left:r.left, right:r.right,
      textRects: rects.map(r=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom})),
      clipped: r.left < -0.5 || r.right > innerWidth + 0.5 || rects.some(r=>r.left < -0.5 || r.right > innerWidth + 0.5)};
  }
  return {items,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
    scrollX,fonts:document.fonts.status};
}"""


def assert_dossier_bounds(page, case, mode, locale, output):
    selectors={'state':'.state','title':'.decision-narrative h1','identity':'.meta',
               'product':'.summary-identity'}
    if mode=='simulated':selectors.update(warning_ar='.warning strong[lang="ar"]',warning_en='.warning strong[lang="en"]')
    labels=locale_bundle(locale)['synthetic_labels'];reports=[]
    output.parent.mkdir(parents=True,exist_ok=True)
    for position in ('initial','leftmost'):
        if position=='leftmost':
            page.evaluate("window.scrollTo({left: -(document.documentElement.scrollWidth - innerWidth), top:0, behavior:'instant'})")
        report=page.evaluate(MEASURE,selectors);reports.append(report)
        page.screenshot(path=str(output.with_name(output.name+'-'+position+'.png')),animations='disabled')
    output.with_suffix('.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    for report in reports:
        assert report['fonts']=='loaded'
        for name,item in report['items'].items():
            assert not item.get('missing'),name
            assert item['text'],name
            assert not item['clipped'],(name,item)
        assert case.id in report['items']['identity']['text']
        if mode=='simulated':
            assert report['items']['warning_en']['text']==labels['en']
            assert report['items']['warning_ar']['text']==labels['ar']
        else:
            for label in labels.values():expect(page.locator('body')).not_to_contain_text(label)
        assert report['scrollWidth']<=report['width']
