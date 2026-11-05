"""Reproduce known answers, threshold/missing-input probes and UI audit."""
import copy
import json
from pathlib import Path
import panel
from streamlit.testing.v1 import AppTest

b = Path(__file__).resolve().parent
results = {}
for ticker in ['COST', 'GATX', 'NVDA', 'JPM']:
    r, report = panel.run(ticker)
    memos = {i: (b/'outputs'/f'{ticker}_{s}_memo.md').read_text(encoding='utf-8') for i,s in [('Buffett','buffett'),('Cathie Wood','wood'),('Burry','burry')]}
    assert not panel.audit_all(memos, report), panel.audit_all(memos, report)
    for investor in memos:
        probe = dict(memos); probe[investor] += '\nUnsupported number 987654321.123%'
        flags = panel.audit_all(probe, report)
        assert flags and flags[0]['investor'] == investor
    results[ticker] = r['panel']
    if ticker == 'GATX':
        assert list(r['panel']['Buffett'].values()) == ['fail','not known','not known']
        assert list(r['panel']['Cathie Wood'].values()) == ['fail','not known']
        assert list(r['panel']['Burry'].values()) == ['pass','fail']
    if ticker == 'COST':
        assert list(r['panel']['Buffett'].values()) == ['pass']*3
        assert list(r['panel']['Cathie Wood'].values()) == ['fail','not known']
        assert list(r['panel']['Burry'].values()) == ['pass']*2
        assert f"{r['revenue_cagr']:.2%}" == '7.51%'
        assert [f"{x['liabilities_to_equity']['value']:.2f}" for x in r['rows']] == ['2.11','1.75','1.96','1.64','1.49']
        assert all(x['research_and_development']['value'] is None for x in r['rows'])
        skill = b/'.agents/skills/cathie-wood-edgar/SKILL.md'
        original = skill.read_text(encoding='utf-8')
        try:
            skill.write_text(original.replace('growth_threshold: 0.15','growth_threshold: 0.05'),encoding='utf-8')
            pr, probe_report = panel.run('COST')
            assert list(pr['panel']['Cathie Wood'].values()) == ['pass','not known']
            (b/'outputs/COST_threshold_probe.md').write_text(probe_report,encoding='utf-8')
        finally:
            skill.write_text(original,encoding='utf-8')
            panel.run('COST')
        missing = copy.deepcopy(r['rows']); missing[0]['revenue']['value'] = None
        assert list(panel.cathie_checks(missing,.15)[0].values()) == ['not known','not known']
        assert list(panel.cathie_checks(r['rows'][:4],.15)[0].values())[0] == 'not known'

app = AppTest.from_file(str(b/'streamlit_app.py')).run(timeout=30)
assert not app.exception, app.exception
assert len(app.columns) == 3
for index in [0,1,2]:
    editor = app.text_area[index]
    original = editor.value
    editor.set_value(original+'\n987654321.123%').run()
    assert any('Unsupported memo numbers' in x.value for x in app.error)
    app.text_area[index].set_value(original).run()
app.text_input[0].set_value('GATX').run(timeout=30)
assert not app.exception
assert any('All three memos pass' in x.value for x in app.success)
(b/'evidence/lab19_verification.json').write_text(json.dumps({'status':'PASS','checks':results,'probes':'COST threshold edited in skill and restored; missing inputs; unsupported token independently in all three memos and UI; COST/GATX AppTest loads','ui_method':'Streamlit AppTest; no screenshot review claimed'},indent=2),encoding='utf-8')
print('PASS: known answers, missing inputs, skill threshold probe, all memo audits and Streamlit interactions')
