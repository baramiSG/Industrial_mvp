import hashlib, json, sys
from pathlib import Path
from unittest.mock import patch
from contextlib import nullcontext
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.data_repository import public_cases
from ior_mvp.decision_engine import analyze
from ior_mvp.graph.projection import build_repository_projection, discover_inputs, _engine_run_id
from ior_mvp.graph.artifact import canonical_bytes, validate_projection, load_projection, projection_id

def require(ok, message):
    if not ok: raise ValueError(message)
root = Path.cwd().resolve()
role = sys.argv[1]
require(role in ('predecessor', 'source', 'final'), 'role')
require(PROJECT_ROOT.resolve() == root, 'project root')
inputs = discover_inputs(root)
p = build_repository_projection(root)
q = build_repository_projection(root)
validate_projection(p); validate_projection(q)
b = canonical_bytes(p)
require(b == canonical_bytes(q), 'double build')
require(inputs == discover_inputs(root) == p.inputs, 'input drift')
run, authority = _engine_run_id(root, inputs)
require(p.projection_id == projection_id(inputs, as_of=p.as_of), 'projection identity')
require(p.engine['engine_run_id'] == run and p.engine['authority_basis_sha256'] == authority, 'engine identity')
if role in ('predecessor', 'final'):
    stored = load_projection(root / 'data/graph')
    pointer = json.loads((root / 'data/graph/current.json').read_bytes())
    stored_bytes = (root / 'data/graph/projections' / pointer['projection_id'] / 'projection.json').read_bytes()
    require(b == stored_bytes == canonical_bytes(stored), 'stored reproduction')
rows = {}
context = nullcontext() if role == 'final' else patch('ior_mvp.graph.repository.graph_projection', return_value=p)
with context:
    for case in sorted(public_cases()):
        rows[case] = {'public_before': analyze(case, 'public'),
                      'simulated': analyze(case, 'simulated'),
                      'public_after': analyze(case, 'public')}
require(len(rows) == 11 and inputs == discover_inputs(root), 'case/input closure')
print(json.dumps({'role': role, 'graph': json.loads(b), 'analyses': rows,
                  'canonical_sha256': hashlib.sha256(b).hexdigest(), 'canonical_bytes': len(b)},
                 ensure_ascii=False, sort_keys=True, allow_nan=False))
