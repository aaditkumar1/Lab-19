# Lab 19 - Legend Panel

Aadit Kumar | November 5, 2026

**Decision: use the panel only as a preliminary Project 2 screen, conditional on checking missing data, sector suitability, valuation and total portfolio exposure before investing.**

The question: When three investors' skills read the same annual filing facts, where do they agree, where do they split - and would I trust the panel?

## Company selection

I use **AVUV -> GATX**, following my selected Project 2 fund, Avantis U.S. Small Cap Value ETF. The [issuer's latest portfolio data](https://www.avantisinvestors.com/avantis-investments/en-us/avantis-us-small-cap-value-etf/) dated November 4, 2026 lists GATX first at 1.00%. The embedded issuer holdings table is preserved in [saved source HTML](evidence/AVUV_issuer_page.html), with a readable [holdings extract](evidence/AVUV_holdings_evidence.md) and [selection metadata](evidence/AVUV_selection.json). The older September quarterly fact sheet lists Matson first; I use the more recent daily issuer holdings. GATX has eligible annual 10-K facts, so no next-largest-company substitution is needed.

## Same facts, different questions

The [shared calculation driver](panel.py) passes the same five fiscal periods to each screen. [Buffett](.agents/skills/buffett-edgar/SKILL.md) emphasizes historical earning power; [Cathie Wood](.agents/skills/cathie-wood-edgar/SKILL.md) emphasizes growth and research intensity; [Burry](.agents/skills/burry-edgar/SKILL.md) emphasizes cash support and balance-sheet skepticism. These are simplified educational adaptations inspired by [FAskills Wood](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md) and [FAskills Burry](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md), not their actual recommendations or full investment processes. The classroom thresholds come from the assignment.

## Known-answer verification and threshold probe

The [computed COST report](outputs/COST_report.md) reproduces Buffett's three passes, Wood's growth failure at 7.51% with R&D not found and its check not known, and Burry's two passes. Liabilities / equity rounds to 2.11, 1.75, 1.96, 1.64 and 1.49 in chronological order. The answer key is used only in verification assertions, never as the app's inputs.

I changed growth_threshold in Wood's SKILL.md from 0.15 to 0.05 and reran the shared script: COST's growth check became pass; R&D stayed not known. The [probe report](outputs/COST_threshold_probe.md) preserves the output. The original threshold is restored.

**Threshold kept: 15%; retain the stated growth mandate instead of tuning the rule to make Costco pass.** A changed classification with unchanged facts demonstrates sensitivity to the screen designer's preferences, not a change in the business.

## My company: bull and bear

The [GATX report](outputs/GATX_report.md) prints each annual input, tag, filing date, accession, formula and check. The five selected fiscal years end December 31, 2021 through December 31, 2025. No later annual period is assumed.

| Investor | Check | Result |
|---|---|---|
| Buffett | ROE at least 15% every year | fail |
| Buffett | Owner earnings positive every year | not known |
| Buffett | Owner earnings grew first to last | not known |
| Cathie Wood | Revenue CAGR at least 15% | fail - 8.47% |
| Cathie Wood | Latest R&D / revenue at least 5% | not known |
| Burry | OCF at least net income every year | pass |
| Burry | Latest liabilities / equity no more than 2 | fail - 5.22 |

Capital spending is not found under the permitted tags for the latest two periods; their owner earnings cannot be calculated. Earlier owner earnings is negative. The inherited Lab 18 check function returns not known whenever any required value is missing, so the full-history owner-earnings checks remain not known even though the observed negative years are already unfavorable evidence. R&D is not found in all selected years and no estimate replaces it.

**Bull case - two sentences:** GATX's operating cash flow covers net income throughout the selected history, supporting the cash backing of reported earnings. Revenue grows and ROE improves across the endpoints, providing reasons to investigate further despite the failed screening hurdles.

**Bear case - two sentences:** Revenue growth misses Wood's threshold, ROE misses Buffett's hurdle, and latest liabilities relative to equity exceeds Burry's ceiling. Missing recent capital-spending inputs prevent a complete owner-earnings assessment, while the observed early owner-earnings values are negative.

The separate memo verdicts are [Buffett: watch it](outputs/GATX_buffett_memo.md), [Wood: pass on this growth screen](outputs/GATX_wood_memo.md), and [Burry: watch it with a leverage concern](outputs/GATX_burry_memo.md). They agree that the available evidence does not justify an ownership conclusion; their reasons differ. A leverage failure does not itself establish insolvency, and a growth-screen failure does not prove the shares are overvalued.

**My decision: only with a condition - use the panel to prioritize Project 2 diligence, preserve its gaps, and require capital-spending reconciliation, financing/sector review, valuation and portfolio-overlap checks before acting.** The screen of one holding does not establish whether AVUV itself is an attractive fund.

## Explain Cathie Wood's actual code

Open cathie_checks in panel.py:

1. complete checks whether the selected history contains five periods.
2. first and last read the earliest and latest revenue values; an empty history gives None.
3. growth remains None for incomplete history, missing endpoint revenue, a nonpositive starting revenue or negative ending revenue. Otherwise it computes (last / first) ** (1 / 4) - 1: five annual observations span four growth intervals.
4. rd reads latest R&D, preserving a missing value as None.
5. intensity stays None if R&D or latest revenue is missing, or latest revenue is nonpositive. Otherwise it divides R&D by revenue.
6. checks calls status for each derived value. status returns not known for None; otherwise the comparison returns pass or fail. Equality passes at the threshold.
7. return sends the checks and calculated values back to the shared driver. No missing input is replaced with zero.

Latest-year intensity can still be known with a shorter history if its latest inputs exist; CAGR requires the full history. Missing intermediate revenue alone does not block endpoint CAGR. Raw R&D is displayed as not found, while an unavailable derived ratio/check is displayed as not known.

## Sell-off interpretation

Using the assignment's sell-off as a supplied scenario, Wood's framework would investigate whether falling prices improve a long-term innovation opportunity while testing demand, adoption and research productivity. Burry's framework would investigate whether deteriorating cash conversion or hidden obligations explain the decline and challenge consensus expectations. Neither persona's page establishes what the actual investor traded today; a price drop alone proves neither a bargain nor a short thesis. This exercise does not independently certify the assignment's intraday market percentages.

## Learn and reflect

An agent panel assigns separate analytical roles to a common evidence packet, then compares their conclusions. Here the roles are implemented through three skills, common deterministic arithmetic and three separately written AI educational memos; the app displays saved memos rather than launching autonomous models at runtime. The memos are not independent human experts or statistical votes: they share evidence and were written with the same AI assistant.

The personas disagree because their objectives and evidence requirements differ. GATX's cash backing passes Burry's annual comparison while its latest liabilities / equity fails his leverage ceiling. Wood rejects its growth profile, while Buffett highlights weak ROE and incomplete owner-earnings evidence. A common dataset can support distinct questions without contradictory arithmetic.

The COST probe shows that the threshold embodies a preference. Lowering it changes a label without supplying new evidence. I should fix rules before comparing companies, preserve unknowns, inspect disagreements and avoid majority voting as an investment decision.

Base interpretation: GATX warrants caution and additional diligence rather than a mechanical ownership decision. Upside hypothesis: cash generation remains supportive and capital investment produces durable earning power; the panel cannot quantify that outcome. Downside hypothesis: weaker earnings or cash generation increases pressure from liabilities. Thesis-breaking evidence for the constructive case would include materially impaired cash generation combined with an inability to refinance obligations, or a restatement invalidating the supporting facts. These are qualitative scenarios, not modeled probabilities or return estimates.

Doing nothing beyond retaining diversified fund exposure is a credible alternative to adding a concentrated stock position. Before any stock addition, assess valuation, fund overlap, liquidity needs, taxes, fees and concentration; the panel does not contain those inputs. Review each annual filing and investigate new failures or unresolved gaps before changing the decision.

## Evidence and honesty

[Verification results](evidence/lab19_verification.json) record the COST match, missing-input tests, actual skill-file threshold edit and restoration, and an unsupported-number injection independently into all three memo editors. The same numeric whitelist audits all memos and identifies investor and line. It cannot detect a printed number assigned to the wrong metric, false qualitative claims or all spelled-out numbers.

The raw SEC snapshots and their SHA-256 download metadata are retained in evidence/. COST and JPM reuse the Lab 18 snapshots downloaded November 3, 2026; GATX was retrieved November 5, 2026. NVDA is retained only as a supplemental example from the earlier working version, not the selected company. As-of filtering excludes later filings but cannot reconstruct data absent from a saved snapshot. Thus COST is a reproducible saved-facts run, not a claim that its source was freshly downloaded today. No estimates replace missing facts. JPM is retained as an extra missing-capex and sector-suitability example, not the selected fund company.

The extraction preserves Lab 18's USD, exact 10-K, full-year duration filter, tag precedence and latest-filing selection per metric. Ratios use year-end equity. Owner earnings is OCF less total capex, not a maintenance-capex estimate. Liabilities is an instant; R&D is an annual flow. Only standard companyfacts tags are searched: not found means absent under this extraction policy, not necessarily undisclosed anywhere in a filing. Different metrics may come from different comparative filings; provenance makes this visible.

These written responses prepare the partner discussion, code explanation and reflection. They do not claim a partner exchange, quiz attempt, or no-AI oral exercise occurred. Brightspace and GitHub submission remain the student's actions.

## Submission links

Upload the entire Lab_19 folder, including the hidden .agents directory, evidence and outputs, as browsable files to GitHub. Submit links to this write-up, streamlit_app.py, panel.py, all three SKILL.md files, and the COST/GATX reports and memos. No GitHub URL is invented here; create the links after uploading. See README.md for local run commands.
