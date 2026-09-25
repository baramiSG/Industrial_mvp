from itertools import product
import pytest
from playwright.sync_api import expect
from browser_tests.harness import CASES,LOCALES,STEEL,POLYPROPYLENE,Viewport,run_axe,format_axe_violations
from browser_tests.pages import goto_portfolio,select_case,locale_bundle
from browser_tests.executive_pages import goto_executive

pytestmark=pytest.mark.e2e
CONSUMERS=('analyst-public','analyst-simulated','executive-signal')
VIEWPORTS=(Viewport('mobile-390',390,844),Viewport('tablet-1024',1024,768),Viewport('desktop-1440',1440,1000))


def open_chart(page,case,locale,consumer):
    if consumer=='executive-signal':goto_executive(page,case,locale,'SIGNAL')
    else:
        mode=consumer.split('-')[1];goto_portfolio(page,mode,locale);select_case(page,case,mode,locale)
    page.evaluate('async()=>{await document.fonts.ready}')
    return page.locator('.chart-wrap').locator('xpath=ancestor::article[1]')

@pytest.mark.parametrize(('case','locale','consumer'),tuple(product(CASES,LOCALES,CONSUMERS)))
def test_trade_native_data_matches_entire_public_source(browser_session,case,locale,consumer):
    page=browser_session.page
    before=page.request.get(f'/api/opportunities/{case.id}?mode=public').json()
    card=open_chart(page,case,locale,consumer)
    strings=locale_bundle(locale)['strings']
    expect(card.locator('.trade-scale-note')).to_have_text(strings['trade.scale_note'])
    expect(card.locator('details > summary')).to_have_text(strings['trade.data_summary'])
    assert card.locator('details').get_attribute('open') is None
    card.locator('summary').click()
    expect(card.locator('caption')).to_have_text(strings['trade.data_caption'])
    expected=[]
    for row in sorted(before['trade'],key=lambda item:item['year']):
        cells=[str(row['year'])]
        for key,unit in [('imports_usd_m','USD m'),('imports_kt','kt')]:
            value=row.get(key)
            if isinstance(value,(int,float)) and not isinstance(value,bool):
                formatted=page.evaluate("({value,locale})=>new Intl.NumberFormat(locale==='ar'?'ar-SA-u-nu-latn':'en-US-u-nu-latn',{maximumFractionDigits:1}).format(value)",{'value':value,'locale':locale.code})
                cells.append(formatted+' '+unit)
            else:cells.append(strings['trade.data_unavailable'])
        expected.append(cells)
    actual=card.locator('tbody tr').evaluate_all('rows=>rows.map(r=>[...r.cells].map(c=>c.textContent.trim()))')
    assert actual==expected
    assert page.request.get(f'/api/opportunities/{case.id}?mode=public').json()['real_decision']==before['real_decision']
    if consumer=='analyst-simulated':
        for label in locale_bundle(locale)['synthetic_labels'].values():expect(page.locator('body')).to_contain_text(label)

@pytest.mark.parametrize(('case','locale','consumer','viewport'),tuple(product((STEEL,POLYPROPYLENE),LOCALES,CONSUMERS,VIEWPORTS)))
def test_trade_keyboard_data_remains_readable_at_narrow_width(browser_session,case,locale,consumer,viewport):
    page=browser_session.page;card=open_chart(page,case,locale,consumer);summary=card.locator('summary')
    summary.focus();page.keyboard.press('Shift+Tab');page.keyboard.press('Tab')
    expect(summary).to_be_focused();assert summary.evaluate('n=>n.matches(":focus-visible")')
    assert summary.evaluate('n=>getComputedStyle(n).outlineStyle')!='none'
    page.keyboard.press('Enter');expect(card.locator('details')).to_have_attribute('open','')
    page.keyboard.press('Space');assert card.locator('details').get_attribute('open') is None
    page.keyboard.press('Enter')
    card.scroll_into_view_if_needed()
    out=browser_session.artifact_dir/'trade-data';out.mkdir(parents=True,exist_ok=True)
    page.screenshot(path=str(out/f'{case.slug}-{consumer}-{locale.code}-{viewport.width}.png'),animations='disabled')
    bounds=card.locator('.trade-scale-note,summary,caption,th,td').evaluate_all('''nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();const range=document.createRange();range.selectNodeContents(n);return {text:n.textContent,left:r.left,right:r.right,clip:[...range.getClientRects()].some(t=>t.left<-.5||t.right>innerWidth+.5)}})''')
    assert all(b['text'].strip() and b['left']>=-.5 and b['right']<=viewport.width+.5 and not b['clip'] for b in bounds),bounds
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    violations=run_axe(page)['violations'];assert violations==[],format_axe_violations(violations)
