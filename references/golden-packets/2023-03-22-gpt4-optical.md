# Blind Packet: 2023-03-22 GPT-4 / Optical Interconnect

## As-of Date

2023-03-22 after the A-share close.

Do not use information published after 2023-03-22. Later price action, later earnings reports, later sell-side summaries, and later industry hindsight are out of scope.

## User Task

Treat this as a dated post-close research packet. Apply the installed `market-inflection-radar` workflow from the default stance that there may be no rare opportunity. Use only this packet plus the Skill references to decide whether any candidate merits escalation for personal deep research. Do not assume that every sharp stock move needs an investment-opportunity report.

## Market Tape

Market data source for this packet: Yahoo Finance chart API snapshot pulled for historical OHLCV. Production evaluation should replace this with exchange-verified A-share OHLCV, free-float market cap, turnover, and adjusted price data.

| Asset | Date | Open | High | Low | Close | Volume | Day Change | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Zhongji Innolight / 中际旭创 `300308.SZ` | 2023-03-17 | 32.88 | 35.45 | 32.80 | 34.61 | 27,024,099 | +6.07% | First visible strength after GPT-4 release week. |
| Zhongji Innolight / 中际旭创 `300308.SZ` | 2023-03-20 | 34.65 | 37.38 | 34.62 | 35.82 | 40,527,279 | +3.50% | Continued relative strength. |
| Zhongji Innolight / 中际旭创 `300308.SZ` | 2023-03-21 | 36.00 | 37.20 | 35.12 | 36.83 | 27,890,482 | +2.82% | Up move before GTC news flow fully digested by local market. |
| Zhongji Innolight / 中际旭创 `300308.SZ` | 2023-03-22 | 36.95 | 44.20 | 36.95 | 44.20 | 77,700,043 | +20.01% | Limit-up style large candle; volume about 2.8x the prior session. |

Cross-sectional market context that must be filled by a production data adapter:

- Optical module peer price action for 新易盛, 天孚通信, 源杰科技, 光迅科技, 剑桥科技: requires A-share行情数据库.
- Sector breadth, limit-up count, turnover rank, northbound flow: requires exchange/market database.
- Relative performance versus 创业板指, 通信指数, CPO/光模块指数: requires market database.

## Catalyst Candidates

| Date | Candidate Catalyst | What Was Publicly Known By The As-of Date | Source Grade |
|---|---|---|---|
| 2023-03-14 | OpenAI released GPT-4 | OpenAI described GPT-4 as a large multimodal model and showed materially stronger benchmark performance than GPT-3.5. OpenAI also noted severe capacity constraints for ChatGPT Plus GPT-4 access and API waitlist scaling. | High: OpenAI official release, https://openai.com/index/gpt-4-research/ |
| 2023-03-16 | Microsoft introduced Microsoft 365 Copilot | Microsoft positioned Copilot as combining LLMs with Microsoft Graph and Microsoft 365 apps, making LLM deployment visible in mainstream enterprise software rather than only chatbot demos. | High: Microsoft official blog, https://blogs.microsoft.com/blog/2023/03/16/introducing-microsoft-365-copilot-your-copilot-for-work/ |
| 2023-03-21 | NVIDIA announced DGX Cloud at GTC | NVIDIA presented DGX Cloud as browser-accessible AI supercomputing for training advanced generative AI models, with Oracle first and Microsoft Azure / Google Cloud to follow. | High: NVIDIA Newsroom, https://nvidianews.nvidia.com/news/nvidia-launches-dgx-cloud-giving-every-enterprise-instant-access-to-ai-supercomputer-from-a-browser |
| 2023-03-22 | Domestic AI-infrastructure equities strengthened | The sharp move was concentrated in parts of AI infrastructure. The day’s stock confirmation must be independently verified across the chain with a local market data adapter. | Medium: historical market data snapshot; needs exchange-grade verification. |

## Industry Background Known By That Date

- GPT-4 created a fresh public reference point for frontier-model capability. The key industrial question on 2023-03-22 was no longer only whether chatbots were popular, but how much accelerated compute, data-center networking, and cloud capex would be needed if enterprises and developers started integrating LLMs into real workflows.
- NVIDIA’s 2023 GTC messaging linked generative AI to dedicated AI supercomputing clusters and cloud access. This made the physical stack more visible: GPUs, high-bandwidth networking, storage, and data-center deployment.
- Datacom optical components had already been tied to hyperscale data-center capex before the LLM shock. Cignal AI reported in April 2022 that hyperscale expansion drove datacom optical component revenue growth in 2021, and 400GbE datacom module shipments doubled as large cloud operators transitioned from 100G.
- Optical modules sit in the data-center networking layer. In high-density AI clusters, GPU scale-out increases east-west traffic and raises the importance of high-speed optical interconnect, switch ports, 400G/800G modules, EML/silicon photonics, testing, and advanced packaging.
- As of the latest company annual report available before this date, Zhongji Innolight disclosed high-speed optical module products including 200G, 400G, and 800G, and cited third-party rankings showing a global top-tier share position in optical modules.

## Company / Asset Snapshots

### Zhongji Innolight / 中际旭创 `300308.SZ`

- Business exposure: high-speed optical communication modules for data centers and telecom networks.
- Pre-as-of source base: 2021 annual report was available; 2022 annual report was not yet public on 2023-03-22.
- Available company disclosure before the as-of date stated that the company provided 200G/400G/800G high-speed optical modules and high-end optical solutions.
- Available company disclosure cited LightCounting and Omdia rankings indicating global top-tier market share in 2021.
- Market action on 2023-03-22: close at 44.20 CNY, +20.01%, high equals close, volume 77.7m shares in the Yahoo snapshot. Adjusted/unadjusted treatment and free-float turnover need production market-data verification.

### Other Optical / CPO Chain Names To Pull In Production

- 新易盛 `300502.SZ`: high-speed optical module peer; price, valuation, and 2023-03-22 turnover require market database.
- 天孚通信 `300394.SZ`: optical component / packaging and passive component exposure; price and purity require company disclosure mapping.
- 剑桥科技 `603083.SH`, 光迅科技 `002281.SZ`, 源杰科技 `688498.SH`: potential related names; require purity mapping to data-center high-speed modules versus telecom/passive exposure.
- Overseas comparables and ecosystem assets: Coherent, Lumentum, Marvell, Broadcom, NVIDIA; map only with as-of-date information.

## Valuation And Expectations

Do not invent precise valuation.

- Zhongji Innolight 2023-03-22 closing price: 44.20 CNY in Yahoo snapshot; needs exchange-grade verification and adjustment flag.
- Market cap, free-float market cap, TTM PE, forward PE, sell-side EPS revisions, and consensus target prices: requires Wind / Choice / Bloomberg / FactSet / Tushare Pro / exchange data.
- Key valuation question for the evaluator: whether the price action was still near the beginning of a new expectations curve or already a crowded late-stage extrapolation. Use only data available by 2023-03-22.
- Pre-existing expectation baseline to verify: before GPT-4, optical-module demand expectations were mostly framed around cloud capex recovery, 400G transition, 800G sampling/deployment, telecom, and data-center upgrades. Production data should compare any 2023-03-15 to 2023-03-22 broker EPS/target changes.

## Evidence Table With Source Grade

| Evidence | Dated Availability | Source | Grade | Use In Evaluation |
|---|---:|---|---|---|
| GPT-4 release and capability description | 2023-03-14 | OpenAI official GPT-4 page | High | External AI capability catalyst; validates that the event is not only market rumor. |
| Microsoft 365 Copilot announcement | 2023-03-16 | Microsoft official blog | High | Enterprise adoption signal; helps judge whether LLM demand could spread beyond consumer chat. |
| DGX Cloud announcement | 2023-03-21 | NVIDIA Newsroom | High | AI compute infrastructure signal; connects model demand to cloud supercomputing capacity. |
| Datacom optical component growth and 400GbE transition | 2022-04-13 | Cignal AI press release | Medium-high | Industry bridge between hyperscale capex and optical components; not company-specific order evidence. |
| Zhongji Innolight product and market-share disclosure | 2022-04-25 | 2021 annual report on CNINFO | High | Asset purity and industry position evidence available before the event. |
| 300308.SZ +20.01% on 2023-03-22 | 2023-03-22 | Yahoo Finance chart API snapshot | Medium | Market confirmation; must be replaced with official/paid market data in production. |
| Forum posts saying "ChatGPT concept stocks are hot" | 2023-03-22 | Stock forums / social media | Low | Narrative and crowding only; not a basis for the core thesis. |

## Low-Grade Narrative And Crowding

Low-grade narrative observed around the date:

- Forum language focused on "ChatGPT概念", "CPO", "算力", "光模块", and short-term limit-up lists.
- Retail discussion mixed true infrastructure clues with noisy ticker lists. Some posts treated every AI-adjacent company as interchangeable.
- A production agent should separate chain-specific evidence from narrative heat. Forum热度 can indicate crowding and attention, not industry proof.

Crowding checks to complete with real data:

- 3-day and 5-day turnover percentile for 300308.SZ.
- Number of related names at limit-up on 2023-03-22.
- Whether the core asset moved before or after low-purity followers.
- Fund flow concentration and margin financing changes.

## Bear-Case Material

- GPT-4 was a capability release, not a purchase order for optical modules.
- Cloud capex was still under scrutiny in early 2023 after a 2022 technology drawdown; hyperscaler budget timing could lag enthusiasm.
- Optical module demand depends on data-center architecture and procurement cycles; more AI usage does not mechanically translate into immediate 800G revenue.
- Product mix and customer concentration can create volatility; exact exposure to top AI cloud customers requires disclosure or channel checks.
- Supply chain capacity, price erosion in mature modules, EML/silicon photonics yield, and competitive response could dilute profit translation.
- A single limit-up candle can reflect thematic trading; it needs corroboration from purity, industry evidence, and early-stage price location.

## Missing Evidence / Falsification Checklist

- Verify 2023-03-22 OHLCV, free-float turnover, market cap, PE, and relative-strength ranking from exchange-grade data.
- Pull all company announcements and IR interactions for 300308.SZ available through 2023-03-22.
- Pull 2022 interim / Q3 reports and any disclosed 800G customer or shipment commentary available before 2023-03-22.
- Check whether sell-side EPS revisions after GPT-4 but before 2023-03-22 existed, and whether they changed optical-module demand assumptions.
- Verify whether 800G demand was still in sampling, qualification, or volume deployment for relevant customers as of the date.
- Look for high-grade contrary evidence: hyperscaler capex cuts, order delays, inventory glut, customer concentration risk, or pricing pressure.
- Confirm whether low-purity back-row names were leading the move. If the move was mainly low-purity speculation, downgrade the setup.
