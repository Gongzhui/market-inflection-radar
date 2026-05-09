from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from .sources import (
    SourceQueryResult,
    build_default_registry,
    collect_source_results,
)


DEFAULT_DAILY_THEMES = (
    "AI compute optical modules CPO accelerators",
    "AI memory DRAM HBM storage",
    "semiconductor export controls tariffs AI supply chain",
    "hyperscaler capex AI datacenter power cooling grid",
    "robotics embodied AI sensors actuators",
    "biotech platform breakthrough obesity GLP-1 oncology",
    "new energy storage battery materials copper uranium",
)


@dataclass(frozen=True)
class ThemeScan:
    theme: str
    results: tuple[SourceQueryResult, ...]


@dataclass(frozen=True)
class DailyScan:
    scan_date: str
    generated_on: str
    adapter: str
    themes: tuple[ThemeScan, ...]
    trading_day_note: str


def previous_trading_day(today: date | None = None) -> tuple[str, str]:
    current = today or date.today()
    candidate = current - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    note = "weekday heuristic; exchange holidays are not modeled"
    return candidate.isoformat(), note


def run_daily_scan(
    *,
    scan_date: str | None = None,
    adapter: str = "live",
    themes: tuple[str, ...] = DEFAULT_DAILY_THEMES,
    limit_per_source: int = 3,
) -> DailyScan:
    if scan_date is None:
        resolved_date, note = previous_trading_day()
    else:
        resolved_date = scan_date
        note = "explicit scan date supplied"

    registry = build_default_registry(adapter)
    scans: list[ThemeScan] = []
    for theme in themes:
        results = collect_source_results(
            date=resolved_date,
            theme=theme,
            registry=registry,
            limit_per_source=limit_per_source,
        )
        scans.append(ThemeScan(theme=theme, results=results))

    return DailyScan(
        scan_date=resolved_date,
        generated_on=date.today().isoformat(),
        adapter=adapter,
        themes=tuple(scans),
        trading_day_note=note,
    )


def render_daily_scan(scan: DailyScan) -> str:
    lines = [
        "# Market Inflection Radar Daily Scan",
        "",
        f"- scan_date: {scan.scan_date}",
        f"- generated_on: {scan.generated_on}",
        f"- adapter: {scan.adapter}",
        f"- trading_day_note: {scan.trading_day_note}",
        "- conclusion_seed: 今日无 S 级机会，除非下列主题经补证后全部通过七闸门。",
        "",
        "## Theme Coverage",
        "",
        "| Theme | Records | Search Required | High Grade | Medium Grade | Unavailable |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    followups: list[str] = []
    for theme_scan in scan.themes:
        records = [record for result in theme_scan.results for record in result.records]
        search_required = [record for record in records if record.evidence_grade == "search-required"]
        unavailable = [record for record in records if record.evidence_grade == "unavailable"]
        high = [record for record in records if record.evidence_grade == "high"]
        medium = [record for record in records if record.evidence_grade in {"medium", "medium-high"}]
        lines.append(
            f"| {theme_scan.theme} | {len(records)} | {len(search_required)} | {len(high)} | {len(medium)} | {len(unavailable)} |"
        )

        for record in search_required[:4]:
            queries = record.metadata.get("queries", [])
            if queries:
                followups.append(f"{theme_scan.theme}: {queries[0]}")

    lines.extend(["", "## Source Detail", ""])
    for theme_scan in scan.themes:
        lines.append(f"### {theme_scan.theme}")
        for result in theme_scan.results:
            grades = _grade_counts(result)
            lines.append(
                f"- {result.source.value}: {len(result.records)} records"
                f" ({', '.join(grades) if grades else 'no records'})"
            )
        lines.append("")

    lines.extend(
        [
            "## Required Web/Search Follow-Up",
            "",
            "Run these only for gate-critical themes before writing an S report. If not run, state that the scan remains an automated source sweep rather than a full manual review.",
            "",
        ]
    )
    if followups:
        for item in followups[:20]:
            lines.append(f"- {item}")
    else:
        lines.append("- No search-required records emitted by the live adapters.")

    lines.extend(
        [
            "",
            "## CLI Default Conclusion",
            "",
            "一句话结论：今日无 S 级机会。",
            "理由：本 CLI 只完成上一交易日产业/催化源扫描；只有在后续补齐高等级证据、早期市场确认、核心资产纯度、赔率位置和反方审查后，才允许升级为 S。",
        ]
    )
    return "\n".join(lines) + "\n"


def _grade_counts(result: SourceQueryResult) -> list[str]:
    counts: dict[str, int] = {}
    for record in result.records:
        counts[record.evidence_grade] = counts.get(record.evidence_grade, 0) + 1
    return [f"{grade}={count}" for grade, count in sorted(counts.items())]
