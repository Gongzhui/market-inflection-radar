# Theme Ontology Schema

Use this schema to structure candidates passed between the CLI, manual research, and reports.

```yaml
theme_id: string
theme_name: string
scan_date: YYYY-MM-DD
market:
  region: string
  session: close
catalyst:
  type: capability_shock | supply_demand_tightening | risk_discount_removal | policy_with_transmission | overseas_leader_mapping | order_validation | other
  date: YYYY-MM-DD
  description: string
  evidence_refs:
    - string
industry_curve:
  affected_market: string
  expected_revision: demand | supply | price | margin | capex | risk_discount | valuation | mixed
  horizon: weeks | quarters | years
  why_huge: string
beneficiary_chain:
  upstream:
    - string
  midstream:
    - string
  downstream:
    - string
assets:
  - ticker: string
    name: string
    region: string
    tier: Core | Mapped | Peripheral
    purity_reason: string
    confirmation:
      price_action: string
      is_first_or_early: boolean
evidence:
  - claim: string
    source: string
    grade: high | medium | low
    date: YYYY-MM-DD
    supports_gate:
      - 1
      - 2
    uncertainty: string
gates:
  huge_industry_space: pass | fail | unknown
  short_term_hard_to_disprove: pass | fail | unknown
  real_external_catalyst: pass | fail | unknown
  early_large_bullish_confirmation: pass | fail | unknown
  high_purity_assets: pass | fail | unknown
  reasonable_odds_position: pass | fail | unknown
  bear_case_not_broken: pass | fail | unknown
anti_hype:
  hard_blocks:
    - string
final_rating: S | A | B | C | Reject
```

## Implementation Notes

- Treat `unknown` as fail for S eligibility.
- Require at least one `Core` asset for S.
- Require at least one high-grade evidence item supporting the catalyst.
- Store low-grade evidence separately when it is only about narrative spread or crowding.
