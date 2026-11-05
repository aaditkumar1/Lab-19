# Lab 19 - Legend Panel

Start with [the completed submission](Lab_19_Submission.md). The selected Project 2 fund is AVUV and its largest company in the issuer holdings dated November 4, 2026 is GATX. COST remains the verification baseline; NVDA and JPM are supplemental examples. The app retains the Lab 18 chart, raw facts, tags, provenance, download/refresh controls and editable memos, and adds the full investor panel and shared audit.

Run from this folder:

```powershell
python -m pip install -r requirements.txt
python panel.py COST
python panel.py GATX
python verify_lab.py
python -m streamlit run streamlit_app.py
```

Saved snapshots need no credentials or network. For another ticker, set SEC_USER_AGENT to your real name and email, then run `python panel.py TICKER --live`. Write each memo from its printed report using the corresponding skill. The app does not generate new memos; missing memos remain visibly incomplete. Download edits to preserve them. After data or threshold changes, review saved memos against the new report.

Wood's skill's growth_threshold setting is executable configuration. Change 0.15 to 0.05, reload, inspect the change, then restore it. The saved probe is in outputs/COST_threshold_probe.md. Thresholds use unrounded values.

Sources accessed November 5, 2026: [SEC API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [Streamlit columns](https://docs.streamlit.io/develop/api-reference/layout/st.columns), [Wood source](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md), [Burry source](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md), and the Avantis issuer holdings linked in the submission. Original Wood/Burry pages and the AVUV issuer HTML are saved in evidence for traceability.

Upload the full extracted folder to GitHub, including .agents; submit browsable file links, not only a ZIP. The archive is a transport copy. Partner/quiz activities are not certified by these files.
