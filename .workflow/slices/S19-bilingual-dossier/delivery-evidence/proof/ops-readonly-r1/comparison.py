from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
J = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def require(ok, message):
    if not ok: raise ValueError(message)
def normalize_graph(raw):
    g = deepcopy(raw); pid = g['projection_id']; run = g['engine']['engine_run_id']
    require(g['counts']['nodes'] == 925 and g['counts']['edges'] == 1045, 'counts')
    decisions = {}
    for n in g['nodes']:
        p = n['properties']
        if n['label'] == 'Decision':
            subject = p['opportunity_id'] if p['mode'] == 'public' else p['scenario_id']
            require(p['mode'] in ('public', 'simulated'), 'decision mode')
            require(n['id'] == p['id'] == f"DEC-{subject}-{p['mode']}-{run}", 'decision formula')
            decisions[n['id']] = f"DEC-{subject}-{p['mode']}-OWN-RUN"
    require(len(decisions) == len(set(decisions.values())) == 22, 'decision bijection')
    counts = Counter()
    for n in g['nodes']:
        if n['id'] in decisions: n['id'] = n['properties']['id'] = decisions[n['id']]
    for e in g['edges']:
        if e['source'] in decisions:
            require(e['type'] in ('DEPENDS_ON', 'CONSTRAINED_BY'), 'decision edge type')
            p = e['properties']; d = p['role'] if e['type'] == 'DEPENDS_ON' else f"{p['need_code']}:{p['variant']}"
            key = 'REL-' + sha256(chr(31).join((e['type'], e['source'], e['target'], d)).encode()).hexdigest()[:20]
            require(e['key'] == p['key'] == key, 'derived relationship key')
            counts[e['type']] += 1
            e['source'] = decisions[e['source']]
            e['key'] = p['key'] = [e['type'], e['source'], e['target'], d]
        require(e['target'] not in decisions, 'unexpected incoming decision')
    require(counts == Counter({'DEPENDS_ON':198, 'CONSTRAINED_BY':110}), 'derived edge inventory')
    for item in g['nodes'] + g['edges']:
        p = item['properties']; require(p['projection_id'] == pid, 'own projection')
        p['projection_id'] = 'OWN-PROJECTION'
        if p.get('derived') is True:
            require(p['engine_run_id'] == run, 'own run'); p['engine_run_id'] = 'OWN-RUN'
    g['projection_id'] = 'OWN-PROJECTION'; g['engine']['engine_run_id'] = 'OWN-RUN'
    g['engine']['authority_basis_sha256'] = 'VERIFIED-INPUT-AUTHORITY'
    del g['inputs'] # compared separately and exactly against the S19 approved input-row binding
    nodes = Counter(J(n) for n in g.pop('nodes')); edges = Counter(J(e) for e in g.pop('edges'))
    return J(g), nodes, edges
require(normalize_graph(old['graph']) == normalize_graph(new['graph']), 'complete graph semantics')
A, B = old['analyses'], new['analyses']
require(len(A) == len(B) == 11 and set(A) == set(B), 'complete case set')
for case in sorted(A):
    originals = [side[case][phase] for side in (A, B) for phase in ('public_before', 'simulated', 'public_after')]
    require(len({J(x['real_decision']) for x in originals}) == 1, 'complete real_decision equality')
    for side in (A, B):
        before, sim, after = (side[case][phase] for phase in ('public_before','simulated','public_after'))
        require(J(before) == J(after), 'public repeat')
        require(before['mode'] == after['mode'] == 'public' and sim['mode'] == 'simulated', 'modes')
        require(before['simulation_decision'] is None and J(before['active_decision']) == J(before['real_decision']), 'public consistency')
        require(J(sim['active_decision']) == J(sim['simulation_decision']), 'simulation consistency')
    for side, raw, version in ((A, old['graph'], '1.6.0'), (B, new['graph'], '1.7.0')):
        for phase in ('public_before','simulated','public_after'):
            require(side[case][phase]['authority']['config_versions']['ui_strings'] == version, 'catalogue transition')
a, b = deepcopy(A), deepcopy(B)
for side, raw in ((a, old['graph']), (b, new['graph'])):
    for case in sorted(side):
        for phase in ('public_before','simulated','public_after'):
            side[case][phase]['authority']['config_versions']['ui_strings'] = 'VERIFIED-CATALOGUE-TRANSITION'
    enablers = {n['id']: n['properties']['scenario_ids'] for n in raw['nodes'] if n['properties'].get('kind') == 'shared_enabler'}
    scenarios = {n['properties']['opportunity_id']: n['id'] for n in raw['nodes'] if n['label'] == 'Scenario'}
    for case in sorted(side):
        require(side[case]['simulated']['simulation_scenario']['scenario_id'] == scenarios[case], 'scenario membership')
    for case in ('SAU-H6-760429', 'SAU-H6-760711'):
        sim = side[case]['simulated']
        for value in (sim, sim['active_decision'], sim['simulation_decision']):
            routes = value['route_hypotheses']
            require(len(routes) == 9 and all(type(r['route_code']) is int and r['route_code'] == i for i,r in enumerate(routes)), 'routes')
            e = routes[8]['shared_enabler']
            require(e['graph_projection_id'] == raw['projection_id'] and scenarios[case] in enablers[e['enabler_id']], 'route8 provenance')
            e['graph_projection_id'] = 'VERIFIED-OWN-PROJECTION'
require(J(a) == J(b), 'full analyses after exactly33 metadata and6 graph-reference allowances')
require(A['SAU-H0-721049']['public_before']['real_decision']['state'] == 'INVESTIGATE', 'steel golden')
for side in (A,B):
    for key in ('real_decision','simulation_decision'):
        d = side['SAU-H0-390210']['simulated'][key]
        require(d['state'] == 'REJECT' and type(d['route_code']) is int and d['route_code'] == 0, 'PP golden')
print('ALL11_COMPLETE_REAL_DECISION_AND_GRAPH_SEMANTICS_PASS')
