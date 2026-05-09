---
name: market-inflection-radar
description: Strict post-close industrial investment inflection scan for rare S-level opportunities. Use when the user asks to run today's market-inflection-radar, run a post-close产业级投资机会拐点扫描, evaluate S-level industrial opportunity candidates, run historical run-date scans, deep-dive a theme, or execute golden-test regression cases. The workflow distinguishes first-confirmed industry expectation-curve upgrades from daily stock movement explanations and defaults to no S-level opportunity unless every gate passes.
---

# Market Inflection Radar

Use this skill as an ultra-low-frequency radar for "产业级预期曲线首次上修并被市场确认" opportunities. Do not use it as a daily stock picker, news explainer, theme heat map, or forum narrative summarizer.

## Non-Negotiable Start

When triggered by a one-line request such as "运行今日 market-inflection-radar", run the CLI before writing any conclusion. Do not produce a report from intuition.

From this skill directory:

```bash
cd scripts
python -m inflection_radar run-today --adapter live
python -m inflection_radar run-date --date YYYY-MM-DD --adapter live
python -m inflection_radar deep-dive --theme xxx --date YYYY-MM-DD
python -m inflection_radar sources list --adapter live
python -m inflection_radar sources query --adapter live --source market --date YYYY-MM-DD --entity MU
python -m inflection_radar collect --adapter live --date YYYY-MM-DD --theme xxx --out /tmp/mir-source-bundle.md
python -m inflection_radar golden-test
python -m inflection_radar blind-packet --case all --output-dir /tmp/mir-blind
```

If running from another working directory, set `PYTHONPATH` to this skill's `scripts/` directory before the same commands.

If the local shell does not expose `python`, use `python3 -m inflection_radar ...` with the same arguments.

## Default Stance

Start from: `今日无 S 级机会`.

Only override that default if at least one candidate passes all seven gates:

1. Industry space is huge.
2. The thesis is hard to disprove in the short term.
3. A real external catalyst changed expectations.
4. The market printed a first or early large bullish confirmation.
5. There are high-purity beneficiary assets.
6. Odds are still reasonable versus price location and crowding.
7. Bear-case review does not break the thesis.

If any gate fails, do not output S. Report the first failed gate and cap the candidate at A/B/C according to `references/scoring-rubric.md`.

## Operating Workflow

1. Run `run-today --adapter live` for a daily request. This command must scan the previous trading day using the built-in daily theme watchlist; do not stop merely because no pre-existing candidate was supplied.
2. Treat the CLI output as an automated source sweep, not a full conclusion. It must show theme coverage, source counts, and `search-required` follow-ups.
3. For production-like scans, run `sources list --adapter live` to confirm public adapters, then run targeted `collect --adapter live --date ... --theme ...` for any theme that looks non-empty or gate-relevant. Use `fixture` only for tests.
4. Read `references/mission.md` and `references/opportunity-definition.md` if the task is ambiguous.
5. For any possible S candidate, load `references/scoring-rubric.md`, `references/evidence-standards.md`, `references/anti-hype-checklist.md`, and `references/report-template.md`.
6. Build an evidence table before writing the rating. High-grade evidence must anchor the core thesis; low-grade evidence may only describe narrative spread or crowding.
7. If a live source returns `search-required`, `unavailable`, or zero records for a gate-critical claim, use available web/search/browser tools to find official or high-grade sources with the scan date as a hard cutoff. Log the query, source, date, and whether it failed. Do not treat a missing source as verified.
8. Apply the anti-hype checklist after the positive case, not before it. A single hard failure there blocks S.
9. Use `references/golden-cases.md` as evaluator-only regression behavior. Do not feed its answer-key language to an agent being forward-tested.
10. For blind validation, generate packets with `python -m inflection_radar blind-packet --case all --output-dir /tmp/mir-blind` and give the target agent only the generated packet plus this Skill. The packet must contain only dated, as-of information, not expected ratings or correct labels. The source packet files live in `references/golden-packets/`.

## Output Rules

For no S-level setup, keep the answer short:

```markdown
一句话结论：今日无 S 级机会。
主要观察：...
被否候选：候选 / 最高评级 / 首个未通过 gate / 需要继续跟踪的证据。
```

For an S-level setup, use `references/report-template.md` exactly as the report skeleton. Include:

- 一句话结论
- 今日触发信号
- 为什么不是普通异动
- 产业空间
- 受益链条
- 核心标的分层
- 证据表
- 反方观点
- 证伪条件
- 拥挤度与时点
- 最终评级

Always phrase the output as research triage, not investment advice or a buy/sell instruction.

## References

- `references/mission.md`: mission, non-goals, and expected behavior.
- `references/opportunity-definition.md`: what counts as an S-level industrial inflection.
- `references/trigger-taxonomy.md`: catalyst taxonomy and trigger patterns.
- `references/scoring-rubric.md`: hard gate system and rating caps.
- `references/evidence-standards.md`: source hierarchy and evidence rules.
- `references/report-template.md`: mandatory S-level report format.
- `references/anti-hype-checklist.md`: hard blocks against hype-driven S ratings.
- `references/golden-cases.md`: evaluator-only regression answer key and blind-test protocol.
- `references/golden-packets/`: blind historical packets for forward testing without answer keys.
- `references/theme-ontology.schema.md`: theme/entity schema for structured candidates.
- `references/data-sources.md`: preferred data source categories and collection order.
