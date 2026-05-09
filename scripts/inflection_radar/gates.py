from dataclasses import dataclass
from typing import Iterable


GATE_ORDER = [
    "huge_industry_space",
    "short_term_hard_to_disprove",
    "real_external_catalyst",
    "early_large_bullish_confirmation",
    "high_purity_assets",
    "reasonable_odds_position",
    "bear_case_not_broken",
]


@dataclass(frozen=True)
class Candidate:
    theme: str
    date: str
    gates: dict[str, bool]
    evidence_grades: list[str]
    has_core_asset: bool
    anti_hype_blocks: list[str]
    expected_rating: str | None = None
    note: str = ""


@dataclass(frozen=True)
class Assessment:
    rating: str
    first_failed_gate: str | None
    passed_all_gates: bool
    reasons: list[str]


def assess_candidate(candidate: Candidate) -> Assessment:
    reasons: list[str] = []
    first_failed = None

    for gate in GATE_ORDER:
        if not candidate.gates.get(gate, False):
            first_failed = gate
            reasons.append(f"failed gate: {gate}")
            break

    passed_all = first_failed is None
    has_high_grade = "high" in {grade.lower() for grade in candidate.evidence_grades}

    if candidate.anti_hype_blocks:
        reasons.append("anti-hype hard block present")
        return Assessment("C", first_failed, False, reasons)

    if not has_high_grade:
        reasons.append("no high-grade core evidence")
        return Assessment("B" if passed_all else "C", first_failed, False, reasons)

    if not candidate.has_core_asset:
        reasons.append("no Core high-purity beneficiary")
        return Assessment("B", first_failed, False, reasons)

    if passed_all:
        return Assessment("S", None, True, ["all seven gates passed"])

    if first_failed in {"real_external_catalyst"}:
        return Assessment("C", first_failed, False, reasons)

    if first_failed in {"early_large_bullish_confirmation", "high_purity_assets"}:
        return Assessment("B", first_failed, False, reasons)

    return Assessment("B", first_failed, False, reasons)


def summarize_candidates(candidates: Iterable[Candidate]) -> str:
    lines = ["一句话结论：今日无 S 级机会。", "", "被否候选："]
    any_candidate = False
    for candidate in candidates:
        any_candidate = True
        assessment = assess_candidate(candidate)
        gate = assessment.first_failed_gate or "none"
        lines.append(
            f"- {candidate.theme} / 最高评级 {assessment.rating} / 首个未通过 gate: {gate} / {candidate.note}"
        )
    if not any_candidate:
        lines.append("- 无可进入七闸门审查的候选。")
    return "\n".join(lines)
