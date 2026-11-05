"""Shared evidence and deterministic checks for the Legend Panel."""
import importlib.util
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('edgar_facts', BASE / '.agents/skills/buffett-edgar/scripts/edgar_facts.py')
facts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(facts)
facts.TAGS.update(liabilities=['Liabilities'], research_and_development=['ResearchAndDevelopmentExpense'])
# Both balance-sheet fields are instants, unlike annual income/cash-flow facts.
original_select = facts.select_fact
def select_fact(data, metric, end, as_of):
    if metric != 'liabilities':
        return original_select(data, metric, end, as_of)
    candidates = [f for f in facts.facts_for(data, 'Liabilities') if facts.eligible(f, as_of) and f['end'] == end and not f.get('start')]
    if not candidates:
        return {'value': None, 'tag': 'not found', 'end': end, 'unit': 'USD'}
    f = max(candidates, key=lambda x: (x['filed'], x.get('accn', '')))
    same = [x for x in candidates if (x['filed'], x.get('accn')) == (f['filed'], f.get('accn'))]
    if len({x['val'] for x in same}) != 1:
        raise ValueError('Conflicting liabilities facts')
    return {'value': f['val'], 'tag': 'us-gaap:Liabilities', 'end': end, 'filed': f['filed'], 'accession': f.get('accn'), 'unit': 'USD'}
facts.select_fact = select_fact

def growth_threshold():
    text = (BASE / '.agents/skills/cathie-wood-edgar/SKILL.md').read_text(encoding='utf-8')
    return float(re.search(r'^growth_threshold: ([0-9.]+)$', text, re.M).group(1))

def cathie_checks(rows, threshold):
    """Explain line by line: missing inputs remain unknown, never zero."""
    complete = len(rows) == 5
    first = rows[0]['revenue']['value'] if rows else None
    last = rows[-1]['revenue']['value'] if rows else None
    growth = None if not complete or first is None or last is None or first <= 0 or last < 0 else (last / first) ** (1 / 4) - 1
    rd = rows[-1]['research_and_development']['value'] if rows else None
    intensity = None if rd is None or last is None or last <= 0 else rd / last
    checks = {f'Revenue CAGR >= {threshold:.0%} first to last': status(growth, lambda x: x >= threshold),
              'Latest R&D / revenue >= 5%': status(intensity, lambda x: x >= .05)}
    return checks, growth, intensity

def status(value, predicate):
    return 'not known' if value is None else ('pass' if predicate(value) else 'fail')

def run(ticker, offline=True, as_of='2026-11-05', user_agent=None, threshold=None):
    result, _ = facts.run(ticker, BASE / 'outputs', user_agent, as_of, offline)
    rows = result['rows']
    threshold = growth_threshold() if threshold is None else threshold
    wood, growth, intensity = cathie_checks(rows, threshold)
    for row in rows:
        l, e = row['liabilities']['value'], row['equity']['value']
        row['liabilities_to_equity'] = {'value': None if l is None or e is None or e <= 0 else l / e, 'tag': 'Liabilities / StockholdersEquity', 'unit': 'ratio'}
        rd, rev = row['research_and_development']['value'], row['revenue']['value']
        row['rd_to_revenue'] = {'value': None if rd is None or rev is None or rev <= 0 else rd / rev, 'tag': 'ResearchAndDevelopmentExpense / revenue', 'unit': 'ratio'}
    cash = [(r['operating_cash_flow']['value'], r['net_income']['value']) for r in rows]
    cash_check = 'not known' if len(rows) != 5 or any(a is None or b is None for a,b in cash) else ('pass' if all(a >= b for a,b in cash) else 'fail')
    burry = {'OCF >= net income every year': cash_check, 'Latest liabilities / equity <= 2': status(rows[-1]['liabilities_to_equity']['value'], lambda x: x <= 2)}
    result.update(panel={'Buffett': result['checks'], 'Cathie Wood': wood, 'Burry': burry}, revenue_cagr=growth, growth_threshold=threshold)
    report = facts.report_text(result)
    report += '\n## Panel inputs and calculations\nUSD millions; ratios dimensionless.\n'
    report += '| Fiscal year end | Liabilities | R&D | R&D / revenue | Liabilities / equity |\n|---|---:|---:|---:|---:|\n'
    for r in rows:
        rd = r['rd_to_revenue']['value']; le = r['liabilities_to_equity']['value']
        report += f"| {r['fiscal_year_end']} | {facts.money(r['liabilities']['value'])} | {facts.money(r['research_and_development']['value'])} | {'not known' if rd is None else f'{rd:.2%}'} | {'not known' if le is None else f'{le:.2f}'} |\n"
    report += f"\nRevenue CAGR = (last / first)^(1/4) - 1: {'not known' if growth is None else f'{growth:.2%}'}.\nGrowth threshold: {threshold:.0%}. R&D threshold: 5%. Liabilities / equity ceiling: 2.\n"
    report += '\n| Investor | Check | Result |\n|---|---|---|\n'
    for investor, checks in result['panel'].items():
        for check, outcome in checks.items():
            report += f'| {investor} | {check} | {outcome} |\n'
    (BASE / 'outputs' / f'{ticker}_panel.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    (BASE / 'outputs' / f'{ticker}_report.md').write_text(report, encoding='utf-8')
    return result, report

def audit_all(memos, report):
    return [dict(investor=investor, **flag) for investor, memo in memos.items() for flag in facts.audit_memo(memo, report)]

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('ticker'); p.add_argument('--live', action='store_true'); p.add_argument('--as-of', default='2026-11-05')
    a = p.parse_args()
    print(run(a.ticker.upper(), not a.live, a.as_of)[1])
