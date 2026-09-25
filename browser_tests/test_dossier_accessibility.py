from itertools import product
import pytest
from playwright.sync_api import expect
from browser_tests.harness import (BrowserSession, STEEL, POLYPROPYLENE, LOCALES, MODES, Viewport, run_axe, format_axe_violations)
from browser_tests.pages import goto_portfolio,select_case,open_dossier_popup,locale_bundle
from browser_tests.dossier_pages import assert_dossier_bounds

pytestmark=pytest.mark.e2e
DOSSIER_VIEWPORTS=(Viewport('mobile-390',390,844),Viewport('tablet-1024',1024,768),Viewport('desktop-1440',1440,1000))

@pytest.mark.parametrize(('case','mode','locale','viewport'),tuple(product((STEEL,POLYPROPYLENE),MODES,LOCALES,DOSSIER_VIEWPORTS)))
def test_dossier_responsive_identity_and_policy_text_bounds(browser_session,case,mode,locale,viewport):
    page=browser_session.page
    goto_portfolio(page,mode,locale);select_case(page,case,mode,locale)
    popup=open_dossier_popup(page,case,mode,locale)
    output=browser_session.artifact_dir/'dossier-bounds'/f'{case.slug}-{mode}-{locale.code}-{viewport.width}'
    assert_dossier_bounds(popup,case,mode,locale,output)
    violations=run_axe(popup)['violations']
    assert violations==[],format_axe_violations(violations)

@pytest.mark.parametrize(('mode','locale'),tuple(product(MODES,LOCALES)))
def test_dossier_keyboard_print_download_and_return(browser_session,mode,locale):
    page=browser_session.page;case=STEEL
    goto_portfolio(page,mode,locale);select_case(page,case,mode,locale)
    popup=open_dossier_popup(page,case,mode,locale)
    popup.evaluate('() => { window.__printRequested=0; window.print=()=>{window.__printRequested+=1;}; }')
    popup.keyboard.press('Tab')
    expect(popup.locator('[data-dossier-print]')).to_be_focused()
    assert popup.locator('[data-dossier-print]').evaluate('n=>n.matches(":focus-visible")')
    popup.keyboard.press('Enter');assert popup.evaluate('window.__printRequested')==1
    popup.keyboard.press('Tab');download=popup.locator('a[download]');expect(download).to_be_focused()
    with popup.expect_download() as event:popup.keyboard.press('Enter')
    payload=event.value.path().read_text()
    import json
    dossier=json.loads(payload);assert dossier['opportunity_id']==case.id and dossier['mode']==mode
    popup.keyboard.press('Tab');expect(popup.locator('[data-dossier-return]')).to_be_focused()
    popup.keyboard.press('Enter')
    expect(popup.locator('#opportunity-select')).to_have_value(case.id)
    expect(popup.locator('html')).to_have_attribute('lang',locale.code)
    expect(popup.locator(f'[data-mode="{mode}"]')).to_have_class(__import__('re').compile(r'\bactive\b'))
