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

## Pillow 12.3.0

- Licence: MIT-CMU
- Source: https://pypi.org/project/pillow/12.3.0/
- Use: deterministic opaque-RGB normalization, lossless WebP encoding and
  pixel comparison for governed visual baselines.

## Playwright Python 1.62.0 Noble container

- Base:
  `mcr.microsoft.com/playwright/python:v1.62.0-noble@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d`
- Use: canonical baseline comparison and reviewer-authorized updates with the
  bundled `chromium-1234`; the application runtime does not use this image.
