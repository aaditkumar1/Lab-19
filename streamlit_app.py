"""Lab 18 UI: imports the skill's single source of arithmetic."""
from datetime import date
import importlib.util
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
import panel
facts = panel.facts

st.set_page_config(page_title='Legend Panel', layout='wide')
st.title('Legend Panel')
st.info('Project 2 fund: AVUV -> GATX. Enter GATX in the sidebar for the selected company; COST is the verification baseline.')
st.caption('Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.')
st.write('A repeatable business-quality screen. Code computes; the AI memo judges.')

with st.sidebar:
    ticker = st.text_input('Ticker', 'COST').strip().upper()
    snapshot = st.checkbox('Use saved SEC snapshot', value=True)
    as_of = st.date_input('Filings available as of', value=date(2026, 11, 5), max_value=date.today())
    user_agent = st.text_input('SEC User-Agent: your name and email', value=os.environ.get('SEC_USER_AGENT', ''), type='password')
    load = st.button('Load / refresh financials', type='primary')
    st.caption('Saved snapshots need no network. Uncheck to download directly from SEC. No API key.')

key = (ticker, snapshot, as_of.isoformat())
if load or st.session_state.get('loaded_key') != key:
    try:
        with st.spinner('Reading SEC facts...'):
            result, report = panel.run(ticker, snapshot, as_of.isoformat(), user_agent)
        st.session_state['result'] = result
        st.session_state['report'] = report
        st.session_state['loaded_key'] = key
    except Exception as exc:
        st.error(str(exc))
        st.info('For a new ticker, uncheck saved snapshot and enter your real SEC User-Agent.')
        st.stop()

result, report = st.session_state['result'], st.session_state['report']
st.subheader(f"{result['ticker']} — {result['company']}")
st.caption(f"As of {result['as_of']} · downloaded {result['source']['retrieved_utc']} · USD millions, except ROE")
rows = result['rows']
chart = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
                       'Owner earnings': None if r['owner_earnings']['value'] is None else r['owner_earnings']['value'] / 1e6,
                       'Net income': None if r['net_income']['value'] is None else r['net_income']['value'] / 1e6} for r in rows]).set_index('Fiscal year end')
st.line_chart(chart, y_label='USD millions')
st.caption('Gaps remain missing; no zero substitution or interpolation is used.')
metrics = list(facts.TAGS) + ['roe', 'owner_earnings']
table = pd.DataFrame([{'Fiscal year end': r['fiscal_year_end'],
                       **{m.replace('_', ' ').title(): facts.display(m, r[m]) for m in metrics}} for r in rows])
st.dataframe(table, hide_index=True, width='stretch')
st.subheader('Investor panel: pass, fail or not known')
st.table(pd.DataFrame([{'Investor': i, 'Check': k, 'Result': v} for i, checks in result['panel'].items() for k,v in checks.items()]))
with st.expander('XBRL tags, filing dates, and accessions'):
    st.markdown(report[report.index('## Tags and provenance'):])
    st.download_button('Download computed facts JSON', json.dumps(result, indent=2), f'{ticker}_facts.json')
    st.link_button('SEC companyfacts source', result['source']['url'])

st.subheader('Independent AI educational memos')
memos = {}
for col, investor, slug in zip(st.columns(3), ['Buffett','Cathie Wood','Burry'], ['buffett','wood','burry']):
    with col:
        st.subheader(investor)
        path = BASE / 'outputs' / f'{ticker}_{slug}_memo.md'
        saved = path.read_text(encoding='utf-8') if path.exists() else ''
        memo = st.text_area(f'{investor} memo', value=saved, height=360, key=f'{ticker}_{slug}')
        memos[investor] = memo
        st.markdown(memo or 'Memo not yet written. Run this skill on the printed report.')
        st.download_button(f'Download {investor} memo', memo, f'{ticker}_{slug}_memo.md')
        if investor == 'Cathie Wood':
            st.caption(f"Growth threshold kept: {result['growth_threshold']:.0%}; retain the lab growth hurdle rather than tune it to COST. Change growth_threshold in her SKILL.md and reload to probe.")
flags = panel.audit_all(memos, report)
if flags:
    st.error('Unsupported memo numbers detected across the panel.')
    st.dataframe(pd.DataFrame(flags), hide_index=True)
elif all(memos.values()):
    st.success('All three memos pass the printed-number audit.')
else:
    st.warning('Incomplete panel: at least one memo is missing.')
st.caption('Numeric support alone cannot verify metric attribution, qualitative truth or numbers spelled out as words. Review memos after refreshing facts or changing thresholds.')
st.download_button('Download printed report', report, f'{ticker}_report.md')
st.text_area('Trust decision', value='Only as a preliminary screen, conditional on verifying gaps, sector suitability, valuation and portfolio concentration before any investment decision.')
