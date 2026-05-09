# Golden Cases

These cases are mandatory regression behavior. `python -m inflection_radar golden-test` must preserve the intent of this file.

This file is an evaluator answer key, not blind-test input. Do not feed this file, the expected ratings, or the required interpretations to an agent being evaluated. For forward tests, generate blind packets with:

```bash
cd scripts
python -m inflection_radar blind-packet --case all --output-dir /tmp/mir-blind
```

Then ask a fresh agent to use `$market-inflection-radar` on only one packet at a time, with an explicit as-of date and no future information. Compare its output to this answer key after it finishes.

The maintained blind packet sources live under `references/golden-packets/`. The CLI copies those Markdown files and prepends only a case-id comment.

## Blind-Test Input Rules

A valid blind packet may include:

- As-of date and market close context.
- Dated primary-source snippets or source stubs available by that date.
- Market data snapshots for leaders, followers, sector breadth, volume, gaps, and relative strength.
- Industry facts visible by that date: orders, prices, capacity, lead times, capex, policy, earnings-call comments, product releases.
- Low-grade narrative samples only as crowding/context evidence.

A valid blind packet must not include:

- Expected rating.
- Gate pass/fail labels.
- Phrases such as "S 级", "应被识别为", "正确解释是", or "不能写成".
- The hidden answer label, except as ordinary factual wording contained in dated source material.
- Evidence published after the as-of date.

## Positive Case 1: GPT-4 and AI Optical Modules

Approximate date: 2023-03-22.

Expected rating: S.

Required interpretation:

- GPT-4 and LLM capability shock triggered a repricing of AI compute demand.
- AI compute demand mapped to high-speed optical modules and related AI networking infrastructure.
- Zhongji Innolight / 中际旭创 should be treated as a high-purity AI optical module leader.
- The first large bullish candle in the high-purity leader is market confirmation.

Forbidden weak interpretation:

- Do not write only "ChatGPT 概念活跃".
- Do not collapse the case into generic AI theme speculation.

## Positive Case 2: AI Memory Supercycle After Trade-War Risk Easing

Approximate date: 2025-05-12.

Expected rating: S.

Required interpretation:

- Trade-war risk easing changed risk appetite, but the deeper thesis is AI-driven DRAM/HBM supply-demand tightness.
- Micron, as an overseas memory leader, gap-up confirmation should map to the memory supply-demand cycle.
- The system should identify an AI memory supercycle, not merely "存储涨价".

Forbidden weak interpretation:

- Do not reduce the case to generic commodity price increase.
- Do not ignore HBM/AI server memory demand.

## Positive Case 3: Core AI Supply Chain Risk-Discount Removal

Approximate date: 2025-05-08.

Expected rating: S.

Required interpretation:

- Zhongji Innolight / 中际旭创 rallied after trade-war panic had punished core AI supply chain assets.
- The correct frame is "risk discount removal for global AI supply chain core assets".
- The asset had a strong underlying AI demand curve before the panic, making the rebound more than a normal oversold bounce.

Forbidden weak interpretation:

- Do not write only "普通超跌反弹".
- Do not ignore the global AI supply-chain core-asset status.

## Negative Case Requirements

The following must never be rated S:

- Ordinary theme rotation without a new external catalyst: maximum B.
- Forum rumor or 小作文-driven move without primary evidence: maximum C.
- Late back-row补涨 after repeated sector climax: maximum C.
- Small-cap story without a visible earnings realization path: maximum B, often C.
- Pure policy slogan without official document, budget, orders, or revenue path: maximum C.

## Regression Expectations

For every golden test, check:

- The rating matches the expected cap.
- The explanation names the industrial curve, not only the stock price.
- The positive cases include high-purity assets and early market confirmation.
- The negative cases fail at least one explicit gate.
- A blind forward test gives the model enough dated evidence to infer the S-level case without seeing this answer key.
