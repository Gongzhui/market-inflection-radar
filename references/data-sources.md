# Data Sources

Use the most primary, dated, and auditable sources available. Prefer direct sources over summaries.

## Collection Order

1. Market confirmation: daily/weekly candles, gap, volume, relative strength, leader versus back-row behavior, overseas leader reaction.
2. Primary catalyst: official release, filing, earnings call, policy document, order announcement, tariff or export-control decision.
3. Industrial evidence: pricing, inventory, utilization, lead time, capacity, orders, capex, customer qualification, product roadmap.
4. Beneficiary mapping: revenue exposure, product mix, customer overlap, capacity, margin sensitivity, valuation sensitivity.
5. Bear case: alternative explanations, already-priced evidence, weak transmission, supply response, valuation/crowding.
6. Low-grade narrative: 雪球, 股吧, 微博, 小作文 only for crowding and narrative spread.

## Preferred Source Categories

- Exchange filings and company announcements.
- SEC filings, annual reports, 10-Q/10-K, earnings call transcripts.
- Official investor relations presentations.
- Official government and regulator documents.
- Recognized industry data vendors and price trackers.
- Hyperscaler and overseas leader capex/guidance disclosures.
- Price and volume data from reliable market-data providers.

## Bundled Public Adapters

Run these through the CLI with `--adapter live`. They require no API key, but they are still best-effort public endpoints and must be treated as source collection, not final judgment.

- `market`: Yahoo Finance chart API for daily OHLCV when symbols are supplied or inferred from a small theme map. Evidence grade is medium because it is a public market-data mirror, not exchange-grade data.
- `global_leaders`: Yahoo Finance daily bars plus SEC filing pointers for U.S.-listed leaders when the ticker can be resolved.
- `announcements`: SEC EDGAR submissions for U.S.-listed companies. Works for tickers such as `MU`, `NVDA`, `AVGO`, `MRVL`.
- `financials`: SEC XBRL companyfacts for U.S.-listed companies. Use as high-grade reported financial evidence, while checking period end and filed date.
- `policy`: Federal Register API search for U.S. official documents.

Use examples:

```bash
python -m inflection_radar sources query --adapter live --source market --date 2025-05-12 --entity MU
python -m inflection_radar sources query --adapter live --source announcements --date 2025-05-12 --entity MU --limit 5
python -m inflection_radar sources query --adapter live --source financials --date 2025-05-12 --entity MU --limit 5
python -m inflection_radar sources query --adapter live --source policy --date 2025-05-12 --keyword tariff --limit 5
python -m inflection_radar collect --adapter live --date 2025-05-12 --theme "AI memory" --out /tmp/mir-source-bundle.md
```

## Daily Scan Watchlist

`run-today --adapter live` does not wait for a user-supplied theme. It resolves the previous trading day by a weekday heuristic and scans this default watchlist:

- AI compute, optical modules, CPO, accelerators.
- AI memory, DRAM, HBM, storage.
- Semiconductor export controls, tariffs, and AI supply chain.
- Hyperscaler capex, AI datacenter power, cooling, and grid.
- Robotics, embodied AI, sensors, actuators.
- Biotech platform breakthroughs, obesity, GLP-1, oncology.
- New energy storage, battery materials, copper, uranium.

The daily scan is deliberately broad and imperfect. Its job is to prove the radar looked across the major high-convexity industrial buckets before saying "no S-level setup." It does not by itself authorize an S rating.

## Search Fallback Requirements

Some critical sources do not have stable unauthenticated public APIs. When the CLI returns `search-required`, `unavailable`, or no records for a gate-critical claim, Codex must use available web/search/browser tools before writing the final rating.

Search fallback is required for:

- A-share official announcements and investor relations: search CNINFO, SSE, SZSE, company IR pages, and official PDFs.
- Earnings-call transcripts and investor days: search company IR, SEC 8-K exhibits, official webcast transcripts, and reputable transcript providers.
- Industry pricing and supply-demand data: search TrendForce, DRAMeXchange, LightCounting, Omdia, Cignal AI, company calls, and official industry releases.
- Chinese policy, export controls, tariffs, and ministry documents: search official ministry, SCIO, NDRC, MIIT, MOFCOM, customs, White House, USTR, BIS, and Federal Register pages as appropriate.
- Consensus estimates, PE, forward PE, turnover, free float, and relative strength: use paid/local market databases if available; otherwise mark as missing and do not overstate.

Search fallback rules:

- Use the scan date as a hard cutoff. Do not use evidence published after the as-of date for historical packets.
- Prefer official and primary sources. Use media only when primary documents are unavailable and label the grade.
- Record failed searches. Missing gate-critical evidence blocks S unless another high-grade source independently supports the same claim.
- Do not convert social media or forum posts into high-grade evidence.

## Source Handling Rules

- Record dates precisely.
- Separate fact, inference, and speculation.
- Do not cite a secondary summary if the primary source is available.
- Do not treat social media as proof of orders, pricing, or policy.
- If a source is inaccessible, label the claim unverified and prevent S unless other high-grade evidence is sufficient.
