"""Finite persisted-output comparison adapted from the retained reviewer probe.

Uses the actual worktree app and stored graph; no patch, repository override,
builder, normalization, or source mutation.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

from fastapi.testclient import TestClient
from ior_mvp.app import app
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.data_repository import public_cases
from ior_mvp.graph.repository import graph_projection

E = Path('/home/barami/projects/industrial-opportunity-resolution-mvp/.autonomous-workflow/overnight-2026-09-23')
R = E / 'reviews/s19-source-readiness-r1'
O = E / 's19/final-print-correction-r1'
W = Path('/home/barami/projects/ior-worktrees/s19')
assert PROJECT_ROOT.resolve() == W.resolve()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
manifest = json.loads((R / 'SEQUENCING-OUTPUTS.json').read_text())
assert sha(R / 'SEQUENCING-OUTPUTS.json') == 'ed7b0f2088d5556458b470aad6de753d233517a91d0244ec34b09b116062c4c5'
assert sha(R / 'SEQUENCING-COMPARISON.json') == '8a0e4410c427ba80fd47ac54ff40e1784e2c64cb73027e3168d40c01c1998846'
for name, digest in manifest.items():
    assert sha(R / name) == digest, name
expected = json.loads((R / 'SEQUENCING-COMPARISON.json').read_text())
expected_rows = {row['file']: row for row in expected['rows']}
assert len(expected_rows) == 88
assert graph_projection().projection_id == 'GRAPH-SAU-2026-09-12-ccd1a2abd05c'
post = {'source': json.loads((O / 'SOURCE-GREEN.json').read_text()),
        'indexes': json.loads((E / 's19/canonical-operation-r1/INPUT-BINDING.json').read_text())['indexes']}
cases = sorted(public_cases())
assert len(cases) == 11
old_css = (O / 'preimages/src/ior_mvp/static/css/dossier.css').read_bytes()
new_css = (O / 'source-green/src/ior_mvp/static/css/dossier.css').read_bytes()
assert hashlib.sha256(old_css).hexdigest() == 'fb10139b6c278f08be68d26534633b6cb966de91533156319a9b92d7b47ef818'
assert hashlib.sha256(new_css).hexdigest() == json.loads((O / 'SOURCE-GREEN.json').read_text())['src/ior_mvp/static/css/dossier.css']
out = O / 'actual-api-outputs-r2'
assert not out.exists()
out.mkdir()
rows = []
with TestClient(app) as client:
    for case in cases:
        for mode in ('public', 'simulated'):
            stem = case + '-' + mode
            paths = {
                'analysis.json': f'/api/opportunities/{case}?mode={mode}',
                'dossier.json': f'/api/opportunities/{case}/dossier?mode={mode}',
                **{f'{locale}.html': f'/api/opportunities/{case}/dossier.html?mode={mode}&locale={locale}' for locale in ('en', 'ar')},
            }
            captured = {}
            for suffix, url in paths.items():
                response = client.get(url)
                name = stem + '-' + suffix
                (out / name).write_bytes(response.content)
                assert response.status_code == 200, (url, response.status_code)
                successor = R / 'sequencing-outputs/successor' / name
                current = R / 'sequencing-outputs/current' / name
                previous_body = successor.read_bytes()
                expected_body = previous_body
                if suffix.endswith('.html'):
                    assert previous_body.count(b'<style>') == previous_body.count(b'</style>') == 1, name
                    assert previous_body.count(old_css) == 1, name
                    start, end = previous_body.index(b'<style>'), previous_body.index(b'</style>')
                    css_start = previous_body.index(old_css)
                    assert start < css_start and css_start + len(old_css) <= end, name
                    expected_body = previous_body.replace(old_css, new_css, 1)
                    assert response.content.count(new_css) == 1, name
                assert response.content == expected_body, name
                before_equal = response.content == current.read_bytes()
                oracle = expected_rows[name]
                assert (previous_body == current.read_bytes()) == oracle['byte_equal'], name
                assert hashlib.sha256(previous_body).hexdigest() == oracle['after_sha256'], name
                rows.append({
                    'file': name, 'url': url, 'http_status': response.status_code,
                    'sha256': sha(out / name), 'bytes': len(response.content),
                    'reviewed_successor_byte_equal': response.content == previous_body,
                    'matches_exact_bound_CSS_only_expectation': True,
                    'pre_generation_byte_equal': before_equal,
                    'prior_generation_differences': oracle.get('differences', []),
                    'current_change': 'one exact embedded CSS substitution' if suffix.endswith('.html') else 'none',
                })
                captured[suffix] = response.content
            analysis = json.loads(captured['analysis.json'])
            dossier = json.loads(captured['dossier.json'])
            old_analysis = json.loads((R / 'sequencing-outputs/current' / (stem + '-analysis.json')).read_bytes())
            assert dossier['public_decision'] == analysis['real_decision'] == old_analysis['real_decision']
assert {row['file'] for row in rows} == set(expected_rows)
assert all(sha(W / name) == digest for name, digest in post['source'].items())
assert all(sha(Path(name)) == digest for name, digest in post['indexes'].items())
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
paths = set(subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=W, env=env).decode().split('\0')) - {''}
assert paths == set(post['source'])
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=W, env=env) == b''
result = {
    'status': 'PASS', 'method': 'Actual unpatched in-process API/TestClient against persisted generated graph in W19',
    'projection_id': graph_projection().projection_id,
    'source_ledger_sha256': sha(O / 'SOURCE-GREEN.json'),
    'reviewer_outputs_sha256': sha(R / 'SEQUENCING-OUTPUTS.json'),
    'reviewer_comparison_sha256': sha(R / 'SEQUENCING-COMPARISON.json'),
    'script_sha256': sha(Path(__file__)), 'responses': len(rows), 'all_status_200': True,
    'all88_match_exact_reviewed_expectations': True,
    'all44_JSON_bodies_byte_equal': True,
    'all44_HTML_only_bound_CSS_substitution': True,
    'CSS_preimage_sha256': hashlib.sha256(old_css).hexdigest(),
    'CSS_postimage_sha256': hashlib.sha256(new_css).hexdigest(),
    'all22_complete_real_public_decisions_equal': True,
    'counts': {kind: {'total': sum(row['file'].endswith(kind) for row in rows), 'pre_generation_byte_equal': sum(row['file'].endswith(kind) and row['pre_generation_byte_equal'] for row in rows)} for kind in ('analysis.json', 'dossier.json', '.html')},
    'source_files_unchanged': len(post['source']), 'indexes_unchanged': len(post['indexes']),
    'rows': rows,
    'sanad': 'Direct actual persisted API responses;44JSON exact equality and44HTML exact equality after the single approved embedded CSS substitution. All other bytes unchanged; no arbitrary normalization or successor override.',
    'muhasabah': 'PASS for actual88 API equivalence after the bounded final-print correction only; corrected targeted/fullfunctional/PDF/canonical/candidate/delivery gates remain separate.',
}
(O / 'ACTUAL-API-COMPARISON-r2.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': result['status'], 'responses': len(rows), 'counts': result['counts'], 'all_reviewed_expectations_exact': True, 'source_files_unchanged': len(post['source']), 'indexes_unchanged': len(post['indexes'])}, indent=2))
