"""Finite S18b corrected canonical128 codec/pixel proof with retained encodings; no browser launch."""
from pathlib import Path
from io import BytesIO
from importlib.metadata import version
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from PIL import Image, ImageChops
from browser_tests.visual_baselines import (
    validate_manifest, compare_paths, BASELINE_ROOT, CANONICAL_IMAGE,
    CHROMIUM_REVISION, LAUNCH_FLAGS, TOLERANCE, _source_hashes, _font_hashes,
)

os.umask(0o077)
OUT = Path('/evidence')
OLD = Path('/old')
BIND = json.loads(Path('/binding.json').read_text())
H = lambda b: hashlib.sha256(b).hexdigest()
def require(ok, label):
    if not ok:
        raise ValueError(label)
def save(name, value):
    with (OUT / name).open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n')

m = validate_manifest()
require(m['change_ref'] == 'S19-BILINGUAL-DOSSIER-2', 'change_ref')
require(m['canonical_image'] == CANONICAL_IMAGE and m['chromium_revision'] == CHROMIUM_REVISION, 'producer identity')
require(m['playwright_version'] == version('playwright') == '1.62.0', 'playwright')
require(m['pytest_playwright_version'] == version('pytest-playwright'), 'pytest-playwright')
require(m['launch_flags'] == list(LAUNCH_FLAGS) and m['tolerance'] == TOLERANCE, 'flags/tolerance')
require(m['source_tree'] == BIND['source_hashes'] == _source_hashes(), 'source closure')
require(m['font_hashes'] == BIND['font_hashes'] == _font_hashes(), 'font closure')
old_manifest = json.loads((OLD / 'manifest.json').read_text())
for key in ('canonical_image', 'chromium_revision', 'browser_version', 'playwright_version', 'pytest_playwright_version', 'launch_flags', 'tolerance', 'font_hashes'):
    require(m[key] == old_manifest[key], 'old producer preservation:' + key)
new_paths = {r['path'] for r in m['entries']}
old_paths = {r['path'] for r in old_manifest['entries']}
require(len(old_paths) == len(new_paths) == 128 and old_paths == new_paths, 'exact128 path preservation')
files = {p.relative_to(BASELINE_ROOT).as_posix() for p in BASELINE_ROOT.rglob('*') if p.is_file()}
require(files == new_paths | {'manifest.json','manifest.sha256'}, '130 exact final visual files')
save('MANIFEST-VALIDATION.json', {'status':'PASS', 'entries':128, 'files':130, 'old_paths':128, 'new_paths':[], 'image_bytes':sum(r['bytes'] for r in m['entries']), 'manifest_sha256':H((BASELINE_ROOT/'manifest.json').read_bytes()), 'producer':{k:m[k] for k in ('canonical_image','chromium_revision','browser_version','playwright_version','pytest_playwright_version','launch_flags')}, 'pillow_version':version('Pillow'), 'source_count':len(m['source_tree']), 'font_count':len(m['font_hashes'])})

ledger = []
for rel in sorted(old_paths):
    old, new = OLD/rel, BASELINE_ROOT/rel
    before_bytes, after_bytes = old.read_bytes(), new.read_bytes()
    with Image.open(old) as a, Image.open(new) as b:
        a.load(); b.load()
        require(a.mode == b.mode == 'RGB' and a.size == b.size, 'old/new decode')
        before_pixels, after_pixels = a.tobytes(), b.tobytes()
        equal = before_pixels == after_pixels
        row = {'path':rel, 'before_sha256':H(before_bytes), 'after_sha256':H(after_bytes), 'before_bytes':len(before_bytes), 'after_bytes':len(after_bytes), 'dimensions':list(a.size), 'before_rgb_sha256':H(before_pixels), 'after_rgb_sha256':H(after_pixels), 'bytes_equal':before_bytes==after_bytes, 'pixels_equal':equal, 'classification':'PIXEL_CHANGE_REQUIRES_INDEPENDENT_REVIEW' if not equal else ('BYTE_IDENTICAL' if before_bytes==after_bytes else 'ENCODING_ONLY_IDENTICAL_PIXELS'), 'metrics':compare_paths(old,new)}
        if not equal:
            diff = OUT/'pixel-diffs'/Path(rel).with_suffix('.png')
            diff.parent.mkdir(parents=True, exist_ok=True)
            ImageChops.difference(a,b).save(diff,format='PNG')
            row['diff_png'] = diff.relative_to(OUT).as_posix()
            row['diff_sha256'] = H(diff.read_bytes())
        ledger.append(row)
save('OLD128-PIXEL-LEDGER.json', ledger)
save('CHANGED-PIXEL-PATHS.json', [r['path'] for r in ledger if not r['pixels_equal']])
print('PIXEL_LEDGER_READY old128=' + str(len(ledger)) + ' changed_pixels=' + str(sum(not r['pixels_equal'] for r in ledger)),flush=True)

def check_codec(entry):
    rel = entry['path']; raw = (BASELINE_ROOT/rel).read_bytes()
    require(raw[:4] == b'RIFF' and raw[8:12] == b'WEBP' and int.from_bytes(raw[4:8],'little')+8==len(raw), 'webp envelope')
    pos=12; chunks=[]
    while pos < len(raw):
        size=int.from_bytes(raw[pos+4:pos+8],'little'); chunks.append(raw[pos:pos+4].decode('ascii')); pos += 8+size+(size%2)
    require(pos==len(raw) and 'VP8L' in chunks and 'VP8 ' not in chunks, 'lossless VP8L')
    with Image.open(BytesIO(raw)) as im:
        im.load(); require(im.mode == 'RGB', 'opaque RGB'); pixels=im.tobytes()
        outputs=[]
        for iteration, quality in enumerate((80,100,100)):
            buffer=BytesIO();im.save(buffer,format='WEBP',lossless=True,quality=quality,method=6,exact=True);encoded=buffer.getvalue()
            with Image.open(BytesIO(encoded)) as again:
                again.load();require(again.mode=='RGB' and again.size==im.size and again.tobytes()==pixels, 'same-input decoded equality')
            if iteration < 2:
                target = OUT / ('quality' + str(quality)) / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(encoded)
            outputs.append(encoded)
        require(outputs[1]==outputs[2]==raw, 'repeat100 and canonical encoded identity')
        return {'path':rel,'dimensions':list(im.size),'mode':im.mode,'chunks':chunks,'canonical_sha256':H(raw),'canonical_bytes':len(raw),'rgb_sha256':H(pixels),'quality80_sha256':H(outputs[0]),'quality80_bytes':len(outputs[0]),'retained80_path':str(Path('quality80')/rel),'retained100_path':str(Path('quality100')/rel),'quality100_sha256':H(outputs[1]),'repeat100_sha256':H(outputs[2]),'decoded80_100_equal':True,'canonical_equals_repeat100':True,'lossless':True,'method':6,'exact':True}

codecs = []
with ThreadPoolExecutor(max_workers=4) as pool:
    for index, row in enumerate(pool.map(check_codec, m['entries']), 1):
        codecs.append(row)
        if index%16==0:print('CODEC_ROWS_PASS '+str(index)+'/128',flush=True)
require(len(list((OUT/'quality80').rglob('*.webp'))) == len(list((OUT/'quality100').rglob('*.webp'))) == 128, 'retain256 encodings')
save('CODEC128.json', codecs)
save('CODEC-PIXEL-RESULT.json', {'status':'MACHINE_CHECKS_PASS_MANUAL_PIXEL_REVIEW_PENDING','codec_rows':len(codecs),'retained_encodings':256,'old_pixel_rows':len(ledger),'changed_pixel_count':sum(not r['pixels_equal'] for r in ledger),'encoded_only_count':sum(r['pixels_equal'] and not r['bytes_equal'] for r in ledger),'byte_identical_count':sum(r['bytes_equal'] for r in ledger),'image_total_bytes':sum(r['canonical_bytes'] for r in codecs),'maximum_image_bytes':max(r['canonical_bytes'] for r in codecs),'pillow_version':version('Pillow'),'no_browser_capture':True,'codec_threads':4,'independent_manual_review_required':True})
print('CANONICAL128_CODEC_AND_OLD128_PIXEL_MACHINE_CHECKS_PASS',flush=True)
