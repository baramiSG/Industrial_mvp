# S19 PDF renderer environment and feasibility receipt

Status: proposed proof environment for S19 plan v2, established by an actual sample render; independent plan review still required. This is a free verification tool overlay, not a product dependency or canonical producer change.

Preparation: after reading R1 and the accepted S18b navigation contract, adopted PDF-toolchain verification and export-context audit personas. Applied the installed PDF skill (actual emitted-PDF rasterization, text and page geometry), Sanad (tool/source/output hashes), al-Muhasibi (separate feasibility from acceptance) and Muhasabah (record two observed print outliers and unverified44PDF gate).

## Observed environment and exact tool

Read-only inspection of the existing canonical image `sha256:938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112` found no Poppler/MuPDF/Ghostscript/ImageMagick executables and no pypdfium2/fitz/pdf2image modules. Its pypdf and Pillow are available. The image identity was unchanged after the proof.

The coordinator's explicit correction task, under the latest owner blocker delegation, authorized bounded free verification-tool preparation. Downloaded the official prebuilt `pypdfium2==5.13.0` wheel through HTTPS, checked its bytes against version-specific PyPI metadata, and extracted it only under the external `planning/s19/renderer-proof/site/` directory. No pip mutation of a project venv, source build, product package/lock edit, image rebuild or paid service occurred.

- Wheel: `pypdfium2-5.13.0-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`.
- Wheel SHA256: `81df25c1ab4c13ff773102d3cbea1967511d079123b067fc077bd0c4d57d91d8`.
- Embedded PDFium: `153.0.7999.0`; `libpdfium.so` SHA256 `224f8ece41f7e35891f11c10073b7b7062d7a18e9ef870586162a85c46130f7d`.
- Exact download URL and method: `renderer-proof/DOWNLOAD-RECEIPT.json`.
- Primary installation/provenance reference: [pypdfium2 on PyPI](https://pypi.org/project/pypdfium2/5.13.0/). Rendering, page-size and tight-character-box APIs: [official Python API](https://pypdfium2.readthedocs.io/en/stable/python_api.html).

## Actual sample proof

`renderer-proof/produce_sample.py` served the actual retained S18a dossier renderer over container-local loopback, waited for local fonts, and emitted four Chromium PDFs: steel×public/simulated×EN/AR. It used the unchanged canonical image, network disabled, source mounted read-only and only the external proof directory writable. The sample is the existing implementation, not an S19 mockup or acceptance result.

`renderer-proof/render_pdf.py` loaded those emitted PDFs with the wheel overlay, extracted text and tight glyph boxes, and rasterized all14 pages at144dpi to PNG. A second independent invocation produced fourteen byte-identical PNGs. `samples/PRODUCTION.json`, `rendered/RENDER-RESULT.json`, `rendered-repeat/RENDER-RESULT.json` and `ENVIRONMENT-CHANGE.json` retain identities and results. The planner visually inspected `steel-public-ar-page-01.png` and `steel-simulated-en-page-01.png`: actual Arabic shaping and English technical text render correctly; old raw-JSON supply and fragmented document layout are visible.

The diagnostic detected **two existing glyph boxes beyond physical page bounds**: simulated AR page4 at the left edge and simulated EN page2 at the right edge. These are retained original print defects for S19 regression coverage, not excused failures or proof that the existing document meets S19. The environment is functional; S19 acceptance remains unrun.

## Reproducible invocation for both exact-candidate proof roots

Use the same immutable image, verified wheel/site overlay and renderer script for each root. Mount that root's44 emitted PDFs read-only at `/input`, verified proof tool/site read-only at `/tool`, and a distinct root-specific output directory writable at `/output`. Keep `--network none`, `--read-only`, a bounded tmpfs, and `PYTHONDONTWRITEBYTECODE=1`. No source checkout or credentials need be mounted for rasterization.

```bash
docker run --rm --network none --read-only \
  --tmpfs /tmp:rw,size=128m \
  -e PYTHONDONTWRITEBYTECODE=1 -e PYTHONPATH=/tool/site \
  -v /absolute/verified-renderer-proof:/tool:ro \
  -v /absolute/candidate-proof-root/pdf:/input:ro \
  -v /absolute/candidate-proof-root/pdf-rendered:/output:rw \
  --entrypoint python \
  sha256:938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112 \
  /tool/render_pdf.py --input /input --output /output
```

Replace the three absolute mounts with recorded proof paths; they are placeholders, not a command to run unchanged. Before execution verify image ID, wheel SHA, binary SHA and script SHA against the accepted packet. Retain per-root PDF/raster/text/geometry hashes and result JSON. Rebuilding the overlay on another Linux x86_64 machine uses the same wheel URL/hash, safe zip extraction and existing exact image; no latest-package lookup or runtime network is needed for rendering. Other platforms require reviewed environment binding, not a source build fallback.

Allowed external preparation paths are `planning/s19/renderer-proof/**`; later proof roots may create only their dedicated `pdf-rendered/**` and proof receipts. The wheel/site are cache/tool artifacts excluded from product Git. A durable `.workflow/slices/S19-bilingual-dossier/delivery-evidence/renderer/` record may contain exact recipe/scripts/tool hashes, environment-change receipt and selected samples/results; retain full44 accepted candidate PDFs/text/metadata separately in the already approved evidence boundary. No product dependency, Makefile, CI producer image, canonical visual policy or test tolerance changes are authorized by this environment packet.

## Bounds and limitations

The current script reports tight nonzero glyph boxes against physical page dimensions at0.01pt tolerance, with zero crop and144dpi rasterization. That detects out-of-page glyphs; it does not certify absence of overlap, safe margins, complete content, correct Arabic reading order or repeated-footer separation. During S19 implementation, the new dossier's declared content/footer regions must be bound to exact print tokens and checked by the allowed dossier tests/diagnostics; visual inspection remains mandatory. Add a deliberately out-of-bounds print fixture as a negative control, preserving the two actual old-dossier outliers as original-defect evidence. A nonzero candidate violation fails the gate; do not return a successful status solely because images were produced.

Every44-case/locale PDF and every page is rasterized. The previously required first-page/full representative/contact-sheet inspection, readable font minima, first-page summary, Arabic identifiers, complete appendices and both labels on every simulated page remain unchanged. The exact S19 acceptance wrapper must fail on any missing document/page or nonzero bounds failure; the prototype renderer is diagnostic and reports counts, so do not confuse its exit0 with acceptance.

Sanad/Muhasabah: PASS for the bounded feasibility record. Tool identity, four emitted PDFs,14 raster pages, repeated equality and two outliers are directly observed. Only two first pages were visually inspected at preparation; no assertion covers unviewed pages or future44PDFs. Primary docs explain the APIs; recorded bytes establish the actual environment. Product, approved packets, indexes and generator roots remain unchanged.
