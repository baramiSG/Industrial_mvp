# Third-party notices — real-browser acceptance

The S06 test harness uses the following development-only components. They are
not loaded by the application at runtime.

## playwright 1.62.0

- Licence: Apache-2.0
- Source: https://pypi.org/project/playwright/1.62.0/
- Use: Python control library and matching Chromium driver.

## pytest-playwright 0.9.0

- Licence: Apache-2.0
- Source: https://pypi.org/project/pytest-playwright/0.9.0/
- Use: pytest fixtures and command-line integration for Playwright.

## axe-core 4.13.0

- Licence: MPL-2.0
- Source: https://registry.npmjs.org/axe-core/-/axe-core-4.13.0.tgz
- Vendored files: `vendor/axe-core-4.13.0/axe.min.js` and upstream `LICENSE`.
- Integrity and acquisition metadata:
  `vendor/axe-core-4.13.0/SOURCE.json`.

The axe distribution is injected from SHA-256-verified local bytes. No test
fetches axe or any other script from a CDN.
