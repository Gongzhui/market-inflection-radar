import argparse

from .blind_packets import packet_ids, render_packet, write_packets
from .daily_scan import DEFAULT_DAILY_THEMES, render_daily_scan, run_daily_scan
from .gates import Candidate, assess_candidate, summarize_candidates
from .golden import golden_cases
from .sources import (
    SourceType,
    build_default_registry,
    build_query_spec,
    collect_source_results,
    parse_source_type,
    render_collection,
    render_query_result,
    render_source_list,
    write_collection,
)


def run_today(args: argparse.Namespace) -> int:
    scan = run_daily_scan(
        adapter=args.adapter,
        limit_per_source=args.limit,
        themes=tuple(args.theme or DEFAULT_DAILY_THEMES),
    )
    print(render_daily_scan(scan), end="")
    return 0


def run_date(args: argparse.Namespace) -> int:
    scan = run_daily_scan(
        scan_date=args.date,
        adapter=args.adapter,
        limit_per_source=args.limit,
        themes=tuple(args.theme or DEFAULT_DAILY_THEMES),
    )
    print(render_daily_scan(scan), end="")
    return 0


def deep_dive(args: argparse.Namespace) -> int:
    candidate = Candidate(
        theme=args.theme,
        date=args.date,
        gates={
            "huge_industry_space": False,
            "short_term_hard_to_disprove": False,
            "real_external_catalyst": False,
            "early_large_bullish_confirmation": False,
            "high_purity_assets": False,
            "reasonable_odds_position": False,
            "bear_case_not_broken": False,
        },
        evidence_grades=[],
        has_core_asset=False,
        anti_hype_blocks=[],
        note="Deep-dive scaffold: fill evidence table before any S rating.",
    )
    print(summarize_candidates([candidate]))
    print("")
    print("请补齐：外部催化、市场确认、高等级证据、核心标的分层、反方观点、证伪条件。")
    return 0


def golden_test(_: argparse.Namespace) -> int:
    failures: list[str] = []
    for case in golden_cases():
        assessment = assess_candidate(case)
        if assessment.rating != case.expected_rating:
            failures.append(
                f"{case.date} {case.theme}: expected {case.expected_rating}, got {assessment.rating}"
            )
        print(f"{case.date} | {assessment.rating} | {case.theme}")
        print(f"  {case.note}")

    if failures:
        print("")
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("")
    print("PASS: golden cases preserve S positives and negative rating caps.")
    return 0


def blind_packet(args: argparse.Namespace) -> int:
    if args.output_dir:
        paths = write_packets(args.case, args.output_dir)
        for path in paths:
            print(path)
        return 0

    if args.case == "all":
        for case_id in packet_ids():
            print(f"- {case_id}")
        return 0

    print(render_packet(args.case))
    return 0


def sources_list(args: argparse.Namespace) -> int:
    try:
        registry = build_default_registry(args.adapter)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2
    print(render_source_list(registry))
    return 0


def sources_query(args: argparse.Namespace) -> int:
    try:
        scan_date = _validate_date(args.date)
        source = parse_source_type(args.source)
        registry = build_default_registry(args.adapter)
        spec = build_query_spec(
            source,
            date=scan_date,
            keyword=args.keyword,
            entities=tuple(args.entity or ()),
            limit=args.limit,
        )
        result = registry.query(source, spec)
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}")
        return 2

    print(render_query_result(result, args.format))
    return 0


def collect(args: argparse.Namespace) -> int:
    try:
        scan_date = _validate_date(args.date)
        registry = build_default_registry(args.adapter)
        selected_sources = _parse_sources(args.source)
        results = collect_source_results(
            date=scan_date,
            theme=args.theme,
            registry=registry,
            sources=selected_sources,
            limit_per_source=args.limit,
        )
        content = render_collection(
            date=scan_date,
            theme=args.theme,
            results=results,
            output_format=args.format,
        )
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}")
        return 2

    if args.out:
        path = write_collection(args.out, content)
        print(path)
    else:
        print(content, end="" if content.endswith("\n") else "\n")
    return 0


def _validate_date(value: str) -> str:
    date.fromisoformat(value)
    return value


def _parse_sources(raw_sources: list[str] | None) -> tuple[SourceType, ...] | None:
    if not raw_sources:
        return None
    return tuple(parse_source_type(raw_source) for raw_source in raw_sources)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m inflection_radar",
        description="Post-close S-level industrial inflection radar CLI scaffold.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_today_parser = subparsers.add_parser("run-today", help="Run today's post-close scan.")
    run_today_parser.add_argument("--adapter", choices=["fixture", "null", "live"], default="live", help="Adapter mode.")
    run_today_parser.add_argument("--theme", action="append", help="Optional theme override. Can be repeated.")
    run_today_parser.add_argument("--limit", type=int, default=3, help="Maximum records per source per theme.")
    run_today_parser.set_defaults(func=run_today)

    run_date_parser = subparsers.add_parser("run-date", help="Run a historical date scan.")
    run_date_parser.add_argument("--date", required=True, help="Scan date in YYYY-MM-DD format.")
    run_date_parser.add_argument("--adapter", choices=["fixture", "null", "live"], default="live", help="Adapter mode.")
    run_date_parser.add_argument("--theme", action="append", help="Optional theme override. Can be repeated.")
    run_date_parser.add_argument("--limit", type=int, default=3, help="Maximum records per source per theme.")
    run_date_parser.set_defaults(func=run_date)

    deep_dive_parser = subparsers.add_parser("deep-dive", help="Prepare a seven-gate deep dive for one theme.")
    deep_dive_parser.add_argument("--theme", required=True, help="Theme name.")
    deep_dive_parser.add_argument("--date", required=True, help="Scan date in YYYY-MM-DD format.")
    deep_dive_parser.set_defaults(func=deep_dive)

    golden_parser = subparsers.add_parser("golden-test", help="Run required regression cases.")
    golden_parser.set_defaults(func=golden_test)

    blind_parser = subparsers.add_parser("blind-packet", help="Emit blind historical packets without answer keys.")
    blind_parser.add_argument("--case", required=True, help="Case id or 'all'.")
    blind_parser.add_argument("--output-dir", help="Directory to write packet markdown files. If omitted, print one packet.")
    blind_parser.set_defaults(func=blind_packet)

    sources_parser = subparsers.add_parser("sources", help="Inspect or query source adapters.")
    sources_subparsers = sources_parser.add_subparsers(dest="sources_command", required=True)

    sources_list_parser = sources_subparsers.add_parser("list", help="List registered source adapters.")
    sources_list_parser.add_argument("--adapter", choices=["fixture", "null", "live"], default="fixture", help="Adapter mode.")
    sources_list_parser.set_defaults(func=sources_list)

    sources_query_parser = sources_subparsers.add_parser("query", help="Query one source adapter.")
    sources_query_parser.add_argument("--source", required=True, help="Source name, e.g. market, announcements, financials, calls, policy, industry_pricing, global_leaders.")
    sources_query_parser.add_argument("--date", required=True, help="As-of date in YYYY-MM-DD format.")
    sources_query_parser.add_argument("--keyword", help="Keyword or theme filter.")
    sources_query_parser.add_argument("--entity", action="append", help="Optional symbol/company/entity filter. Can be repeated.")
    sources_query_parser.add_argument("--limit", type=int, default=20, help="Maximum records to return.")
    sources_query_parser.add_argument("--adapter", choices=["fixture", "null", "live"], default="fixture", help="Adapter mode.")
    sources_query_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    sources_query_parser.set_defaults(func=sources_query)

    collect_parser = subparsers.add_parser("collect", help="Collect a dated source bundle for one theme.")
    collect_parser.add_argument("--date", required=True, help="As-of date in YYYY-MM-DD format.")
    collect_parser.add_argument("--theme", required=True, help="Theme or query phrase.")
    collect_parser.add_argument("--out", help="Optional output path. Prints to stdout if omitted.")
    collect_parser.add_argument("--source", action="append", help="Optional source filter. Can be repeated.")
    collect_parser.add_argument("--limit", type=int, default=20, help="Maximum records per source.")
    collect_parser.add_argument("--adapter", choices=["fixture", "null", "live"], default="fixture", help="Adapter mode.")
    collect_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    collect_parser.set_defaults(func=collect)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
