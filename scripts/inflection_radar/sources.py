from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen


class SourceType(str, Enum):
    MARKET = "market"
    ANNOUNCEMENTS = "announcements"
    FINANCIALS = "financials"
    CALLS = "calls"
    POLICY = "policy"
    INDUSTRY_PRICING = "industry_pricing"
    GLOBAL_LEADERS = "global_leaders"


SOURCE_DESCRIPTIONS: dict[SourceType, str] = {
    SourceType.MARKET: "Point-in-time price, volume, gap, relative strength, valuation, and crowding signals.",
    SourceType.ANNOUNCEMENTS: "Company announcements, exchange filings, order disclosures, and other issuer-level notices.",
    SourceType.FINANCIALS: "Reported financial statements, segment exposure, guidance, margins, and earnings revisions.",
    SourceType.CALLS: "Earnings calls, investor days, conference call transcripts, and management commentary.",
    SourceType.POLICY: "Policy documents, tariff/export-control changes, subsidies, approvals, and regulatory signals.",
    SourceType.INDUSTRY_PRICING: "Commodity, component, capacity, utilization, lead-time, and industry price indicators.",
    SourceType.GLOBAL_LEADERS: "Overseas leader stock moves, filings, product releases, capex, orders, and supply-chain read-throughs.",
}

SOURCE_ALIASES: dict[str, SourceType] = {
    "market": SourceType.MARKET,
    "price": SourceType.MARKET,
    "行情": SourceType.MARKET,
    "announcement": SourceType.ANNOUNCEMENTS,
    "announcements": SourceType.ANNOUNCEMENTS,
    "filing": SourceType.ANNOUNCEMENTS,
    "filings": SourceType.ANNOUNCEMENTS,
    "公告": SourceType.ANNOUNCEMENTS,
    "financial": SourceType.FINANCIALS,
    "financials": SourceType.FINANCIALS,
    "earnings": SourceType.FINANCIALS,
    "财报": SourceType.FINANCIALS,
    "call": SourceType.CALLS,
    "calls": SourceType.CALLS,
    "earnings_call": SourceType.CALLS,
    "transcript": SourceType.CALLS,
    "电话会": SourceType.CALLS,
    "policy": SourceType.POLICY,
    "政策": SourceType.POLICY,
    "industry_pricing": SourceType.INDUSTRY_PRICING,
    "industry-price": SourceType.INDUSTRY_PRICING,
    "pricing": SourceType.INDUSTRY_PRICING,
    "产业价格": SourceType.INDUSTRY_PRICING,
    "global_leaders": SourceType.GLOBAL_LEADERS,
    "global-leaders": SourceType.GLOBAL_LEADERS,
    "leader": SourceType.GLOBAL_LEADERS,
    "overseas": SourceType.GLOBAL_LEADERS,
    "海外龙头": SourceType.GLOBAL_LEADERS,
}


def parse_source_type(raw: str | SourceType) -> SourceType:
    if isinstance(raw, SourceType):
        return raw
    key = raw.strip().lower()
    try:
        return SOURCE_ALIASES[key]
    except KeyError as exc:
        valid = ", ".join(source.value for source in SourceType)
        raise ValueError(f"unknown source '{raw}'. valid sources: {valid}") from exc


@dataclass(frozen=True)
class SourceRecord:
    source: SourceType
    date: str
    title: str
    summary: str
    evidence_grade: str
    entities: tuple[str, ...] = ()
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MarketQuerySpec:
    date: str
    keyword: str | None = None
    symbols: tuple[str, ...] = ()
    limit: int = 20
    source: SourceType = field(default=SourceType.MARKET, init=False)


@dataclass(frozen=True)
class AnnouncementQuerySpec:
    date: str
    keyword: str | None = None
    issuers: tuple[str, ...] = ()
    limit: int = 20
    source: SourceType = field(default=SourceType.ANNOUNCEMENTS, init=False)


@dataclass(frozen=True)
class FinancialReportQuerySpec:
    date: str
    keyword: str | None = None
    companies: tuple[str, ...] = ()
    periods: tuple[str, ...] = ()
    limit: int = 20
    source: SourceType = field(default=SourceType.FINANCIALS, init=False)


@dataclass(frozen=True)
class EarningsCallQuerySpec:
    date: str
    keyword: str | None = None
    companies: tuple[str, ...] = ()
    limit: int = 20
    source: SourceType = field(default=SourceType.CALLS, init=False)


@dataclass(frozen=True)
class PolicyQuerySpec:
    date: str
    keyword: str | None = None
    jurisdictions: tuple[str, ...] = ()
    limit: int = 20
    source: SourceType = field(default=SourceType.POLICY, init=False)


@dataclass(frozen=True)
class IndustryPriceQuerySpec:
    date: str
    keyword: str | None = None
    commodities: tuple[str, ...] = ()
    limit: int = 20
    source: SourceType = field(default=SourceType.INDUSTRY_PRICING, init=False)


@dataclass(frozen=True)
class GlobalLeaderQuerySpec:
    date: str
    keyword: str | None = None
    companies: tuple[str, ...] = ()
    limit: int = 20
    source: SourceType = field(default=SourceType.GLOBAL_LEADERS, init=False)


SourceQuerySpec = (
    MarketQuerySpec
    | AnnouncementQuerySpec
    | FinancialReportQuerySpec
    | EarningsCallQuerySpec
    | PolicyQuerySpec
    | IndustryPriceQuerySpec
    | GlobalLeaderQuerySpec
)


@dataclass(frozen=True)
class MarketQueryResult:
    query: MarketQuerySpec
    records: tuple[SourceRecord, ...]
    adapter_name: str
    source: SourceType = field(default=SourceType.MARKET, init=False)


@dataclass(frozen=True)
class AnnouncementQueryResult:
    query: AnnouncementQuerySpec
    records: tuple[SourceRecord, ...]
    adapter_name: str
    source: SourceType = field(default=SourceType.ANNOUNCEMENTS, init=False)


@dataclass(frozen=True)
class FinancialReportQueryResult:
    query: FinancialReportQuerySpec
    records: tuple[SourceRecord, ...]
    adapter_name: str
    source: SourceType = field(default=SourceType.FINANCIALS, init=False)


@dataclass(frozen=True)
class EarningsCallQueryResult:
    query: EarningsCallQuerySpec
    records: tuple[SourceRecord, ...]
    adapter_name: str
    source: SourceType = field(default=SourceType.CALLS, init=False)


@dataclass(frozen=True)
class PolicyQueryResult:
    query: PolicyQuerySpec
    records: tuple[SourceRecord, ...]
    adapter_name: str
    source: SourceType = field(default=SourceType.POLICY, init=False)


@dataclass(frozen=True)
class IndustryPriceQueryResult:
    query: IndustryPriceQuerySpec
    records: tuple[SourceRecord, ...]
    adapter_name: str
    source: SourceType = field(default=SourceType.INDUSTRY_PRICING, init=False)


@dataclass(frozen=True)
class GlobalLeaderQueryResult:
    query: GlobalLeaderQuerySpec
    records: tuple[SourceRecord, ...]
    adapter_name: str
    source: SourceType = field(default=SourceType.GLOBAL_LEADERS, init=False)


SourceQueryResult = (
    MarketQueryResult
    | AnnouncementQueryResult
    | FinancialReportQueryResult
    | EarningsCallQueryResult
    | PolicyQueryResult
    | IndustryPriceQueryResult
    | GlobalLeaderQueryResult
)


SPEC_BY_SOURCE = {
    SourceType.MARKET: MarketQuerySpec,
    SourceType.ANNOUNCEMENTS: AnnouncementQuerySpec,
    SourceType.FINANCIALS: FinancialReportQuerySpec,
    SourceType.CALLS: EarningsCallQuerySpec,
    SourceType.POLICY: PolicyQuerySpec,
    SourceType.INDUSTRY_PRICING: IndustryPriceQuerySpec,
    SourceType.GLOBAL_LEADERS: GlobalLeaderQuerySpec,
}

RESULT_BY_SOURCE = {
    SourceType.MARKET: MarketQueryResult,
    SourceType.ANNOUNCEMENTS: AnnouncementQueryResult,
    SourceType.FINANCIALS: FinancialReportQueryResult,
    SourceType.CALLS: EarningsCallQueryResult,
    SourceType.POLICY: PolicyQueryResult,
    SourceType.INDUSTRY_PRICING: IndustryPriceQueryResult,
    SourceType.GLOBAL_LEADERS: GlobalLeaderQueryResult,
}

USER_AGENT = "market-inflection-radar/0.3 research-cli contact@example.com"
HTTP_TIMEOUT_SECONDS = 20

THEME_SYMBOLS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("memory", "dram", "hbm", "存储", "内存"), ("MU", "WDC", "STX", "NVDA", "000660.KS", "005930.KS")),
    (("optical", "cpo", "光模块", "gpt-4", "算力"), ("300308.SZ", "300502.SZ", "300394.SZ", "COHR", "LITE", "NVDA")),
    (("ai supply", "supply chain", "供应链", "tariff", "贸易"), ("300308.SZ", "300502.SZ", "NVDA", "AVGO", "MRVL")),
)

SEC_TICKER_ALIASES = {
    "micron": "MU",
    "mu": "MU",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "broadcom": "AVGO",
    "avgo": "AVGO",
    "marvell": "MRVL",
    "mrvl": "MRVL",
    "western digital": "WDC",
    "wdc": "WDC",
    "seagate": "STX",
    "stx": "STX",
}

SEC_FACTS = (
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "NetIncomeLoss",
    "OperatingIncomeLoss",
    "EarningsPerShareDiluted",
    "Assets",
)


class SourceAdapter(Protocol):
    source_type: SourceType
    name: str

    def query(self, spec: SourceQuerySpec) -> SourceQueryResult:
        """Return dated records available as of spec.date."""


class NullSourceAdapter:
    name = "null"

    def __init__(self, source_type: SourceType):
        self.source_type = source_type

    def query(self, spec: SourceQuerySpec) -> SourceQueryResult:
        return make_result(self.source_type, spec, (), self.name)


class FixtureSourceAdapter:
    name = "fixture"

    def __init__(self, source_type: SourceType, records: tuple[SourceRecord, ...]):
        self.source_type = source_type
        self._records = tuple(record for record in records if record.source == source_type)

    def query(self, spec: SourceQuerySpec) -> SourceQueryResult:
        records = [record for record in self._records if self._matches(record, spec)]
        records.sort(key=lambda record: record.date, reverse=True)
        return make_result(self.source_type, spec, tuple(records[: spec.limit]), self.name)

    def _matches(self, record: SourceRecord, spec: SourceQuerySpec) -> bool:
        if record.date > spec.date:
            return False

        keyword = (spec.keyword or "").strip().lower()
        if keyword and not _keyword_matches(keyword, _search_blob(record)):
            return False

        requested_entities = _requested_entities(spec)
        if requested_entities:
            record_entities = {entity.lower() for entity in record.entities}
            metadata_symbols = record.metadata.get("symbols", ())
            record_entities.update(str(symbol).lower() for symbol in metadata_symbols)
            if not record_entities.intersection(requested_entities):
                return False

        return True


class LiveSourceAdapter:
    name = "live"

    def __init__(self, source_type: SourceType):
        self.source_type = source_type

    def query(self, spec: SourceQuerySpec) -> SourceQueryResult:
        try:
            if self.source_type == SourceType.MARKET:
                records = tuple(_query_yahoo_market(spec, SourceType.MARKET))
            elif self.source_type == SourceType.GLOBAL_LEADERS:
                records = tuple(_query_global_leaders(spec))
            elif self.source_type == SourceType.ANNOUNCEMENTS:
                records = tuple(_query_sec_filings(spec))
            elif self.source_type == SourceType.FINANCIALS:
                records = tuple(_query_sec_financials(spec))
            elif self.source_type == SourceType.POLICY:
                records = tuple(_query_federal_register(spec))
            else:
                records = tuple(_search_required_records(self.source_type, spec))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
            records = (
                SourceRecord(
                    source=self.source_type,
                    date=spec.date,
                    title=f"Live adapter error for {self.source_type.value}",
                    summary=f"{type(exc).__name__}: {exc}. Treat this source as unverified and use web/search fallback.",
                    evidence_grade="unavailable",
                    entities=_entities_for_spec(spec),
                    metadata={"fallback": "search_required"},
                ),
            )
        return make_result(self.source_type, spec, records[: spec.limit], self.name)


class SourceRegistry:
    def __init__(self) -> None:
        self._adapters: dict[SourceType, SourceAdapter] = {}

    def register(self, adapter: SourceAdapter) -> None:
        self._adapters[adapter.source_type] = adapter

    def get(self, source: str | SourceType) -> SourceAdapter:
        source_type = parse_source_type(source)
        try:
            return self._adapters[source_type]
        except KeyError as exc:
            raise KeyError(f"source '{source_type.value}' is not registered") from exc

    def query(self, source: str | SourceType, spec: SourceQuerySpec) -> SourceQueryResult:
        source_type = parse_source_type(source)
        if spec.source != source_type:
            raise ValueError(f"spec source '{spec.source.value}' does not match requested source '{source_type.value}'")
        return self.get(source_type).query(spec)

    def list_sources(self) -> tuple[SourceType, ...]:
        return tuple(sorted(self._adapters, key=lambda source: source.value))

    def describe(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for source in self.list_sources():
            adapter = self._adapters[source]
            rows.append(
                {
                    "source": source.value,
                    "adapter": adapter.name,
                    "description": SOURCE_DESCRIPTIONS[source],
                }
            )
        return rows


def build_default_registry(mode: str = "fixture") -> SourceRegistry:
    registry = SourceRegistry()
    normalized = mode.strip().lower()
    if normalized not in {"fixture", "null", "live"}:
        raise ValueError("adapter mode must be 'fixture', 'null', or 'live'")

    records = fixture_records()
    for source in SourceType:
        adapter: SourceAdapter
        if normalized == "null":
            adapter = NullSourceAdapter(source)
        elif normalized == "live":
            adapter = LiveSourceAdapter(source)
        else:
            adapter = FixtureSourceAdapter(source, records)
        registry.register(adapter)
    return registry


def build_query_spec(
    source: str | SourceType,
    *,
    date: str,
    keyword: str | None = None,
    entities: tuple[str, ...] = (),
    limit: int = 20,
) -> SourceQuerySpec:
    source_type = parse_source_type(source)
    normalized_entities = tuple(entity for entity in entities if entity)
    if source_type == SourceType.MARKET:
        return MarketQuerySpec(date=date, keyword=keyword, symbols=normalized_entities, limit=limit)
    if source_type == SourceType.ANNOUNCEMENTS:
        return AnnouncementQuerySpec(date=date, keyword=keyword, issuers=normalized_entities, limit=limit)
    if source_type == SourceType.FINANCIALS:
        return FinancialReportQuerySpec(date=date, keyword=keyword, companies=normalized_entities, limit=limit)
    if source_type == SourceType.CALLS:
        return EarningsCallQuerySpec(date=date, keyword=keyword, companies=normalized_entities, limit=limit)
    if source_type == SourceType.POLICY:
        return PolicyQuerySpec(date=date, keyword=keyword, jurisdictions=normalized_entities, limit=limit)
    if source_type == SourceType.INDUSTRY_PRICING:
        return IndustryPriceQuerySpec(date=date, keyword=keyword, commodities=normalized_entities, limit=limit)
    if source_type == SourceType.GLOBAL_LEADERS:
        return GlobalLeaderQuerySpec(date=date, keyword=keyword, companies=normalized_entities, limit=limit)
    raise ValueError(f"unsupported source '{source_type.value}'")


def collect_source_results(
    *,
    date: str,
    theme: str,
    registry: SourceRegistry,
    sources: tuple[SourceType, ...] | None = None,
    limit_per_source: int = 20,
) -> tuple[SourceQueryResult, ...]:
    selected = sources or tuple(SourceType)
    results: list[SourceQueryResult] = []
    for source in selected:
        spec = build_query_spec(source, date=date, keyword=theme, limit=limit_per_source)
        results.append(registry.query(source, spec))
    return tuple(results)


def make_result(
    source: SourceType,
    spec: SourceQuerySpec,
    records: tuple[SourceRecord, ...],
    adapter_name: str,
) -> SourceQueryResult:
    result_cls = RESULT_BY_SOURCE[source]
    return result_cls(query=spec, records=records, adapter_name=adapter_name)


def render_source_list(registry: SourceRegistry) -> str:
    lines = ["source\tadapter\tdescription"]
    for row in registry.describe():
        lines.append(f"{row['source']}\t{row['adapter']}\t{row['description']}")
    return "\n".join(lines)


def render_query_result(result: SourceQueryResult, output_format: str = "markdown") -> str:
    if output_format == "json":
        return json.dumps(result_to_dict(result), ensure_ascii=False, indent=2)

    lines = [
        f"# Source Query: {result.source.value}",
        "",
        f"- adapter: {result.adapter_name}",
        f"- date: {result.query.date}",
        f"- keyword: {result.query.keyword or ''}",
        f"- records: {len(result.records)}",
        "",
    ]
    if not result.records:
        lines.append("No records returned by this adapter.")
        return "\n".join(lines)

    for record in result.records:
        lines.extend(_render_record(record))
    return "\n".join(lines)


def render_collection(
    *,
    date: str,
    theme: str,
    results: tuple[SourceQueryResult, ...],
    output_format: str = "markdown",
) -> str:
    if output_format == "json":
        payload = {
            "date": date,
            "theme": theme,
            "results": [result_to_dict(result) for result in results],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    lines = [
        "# Market Inflection Radar Source Bundle",
        "",
        f"- date: {date}",
        f"- theme: {theme}",
        "- scope: dated source collection scaffold; not an investment conclusion",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result.source.value}",
                "",
                f"- adapter: {result.adapter_name}",
                f"- records: {len(result.records)}",
                "",
            ]
        )
        if result.records:
            for record in result.records:
                lines.extend(_render_record(record))
        else:
            lines.append("No records returned by this adapter.")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_collection(path: str, content: str) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def result_to_dict(result: SourceQueryResult) -> dict[str, Any]:
    return {
        "source": result.source.value,
        "adapter": result.adapter_name,
        "query": query_to_dict(result.query),
        "records": [record_to_dict(record) for record in result.records],
    }


def query_to_dict(query: SourceQuerySpec) -> dict[str, Any]:
    payload = dict(query.__dict__)
    payload["source"] = query.source.value
    return payload


def record_to_dict(record: SourceRecord) -> dict[str, Any]:
    return {
        "source": record.source.value,
        "date": record.date,
        "title": record.title,
        "summary": record.summary,
        "evidence_grade": record.evidence_grade,
        "entities": list(record.entities),
        "url": record.url,
        "metadata": record.metadata,
    }


def _query_yahoo_market(spec: SourceQuerySpec, source: SourceType) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    symbols = _symbols_for_spec(spec)
    for symbol in symbols:
        record = _fetch_yahoo_daily_record(symbol, spec.date, source)
        if record:
            records.append(record)
        if len(records) >= spec.limit:
            break
    if not records:
        records.extend(_search_required_records(source, spec))
    return records


def _query_global_leaders(spec: SourceQuerySpec) -> list[SourceRecord]:
    records = _query_yahoo_market(spec, SourceType.GLOBAL_LEADERS)
    ticker_map = _sec_ticker_map_safe()
    for ticker in _sec_tickers_for_spec(spec):
        cik = ticker_map.get(ticker.upper())
        if not cik:
            continue
        submissions = _sec_get_json(f"https://data.sec.gov/submissions/CIK{cik}.json")
        recent = submissions.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        docs = recent.get("primaryDocument", [])
        for form, filing_date, accession, doc in zip(forms, dates, accession_numbers, docs):
            if filing_date > spec.date:
                continue
            if form not in {"10-K", "10-Q", "8-K"}:
                continue
            title = f"{ticker.upper()} SEC {form} filed {filing_date}"
            records.append(
                SourceRecord(
                    source=SourceType.GLOBAL_LEADERS,
                    date=filing_date,
                    title=title,
                    summary="SEC filing from an overseas leader that can be used for point-in-time read-throughs.",
                    evidence_grade="high",
                    entities=(ticker.upper(), submissions.get("name", "")),
                    url=_sec_archive_url(cik, accession, doc),
                    metadata={"form": form, "cik": cik, "accession": accession},
                )
            )
            break
    return records[: spec.limit] if records else _search_required_records(SourceType.GLOBAL_LEADERS, spec)


def _query_sec_filings(spec: SourceQuerySpec) -> list[SourceRecord]:
    ticker_map = _sec_ticker_map_safe()
    records: list[SourceRecord] = []
    for ticker in _sec_tickers_for_spec(spec):
        cik = ticker_map.get(ticker.upper())
        if not cik:
            continue
        submissions = _sec_get_json(f"https://data.sec.gov/submissions/CIK{cik}.json")
        company = submissions.get("name", ticker.upper())
        recent = submissions.get("filings", {}).get("recent", {})
        for form, filing_date, accession, doc in zip(
            recent.get("form", []),
            recent.get("filingDate", []),
            recent.get("accessionNumber", []),
            recent.get("primaryDocument", []),
        ):
            if filing_date > spec.date:
                continue
            if form in {"3", "4", "5", "144"}:
                continue
            if spec.keyword and spec.keyword.lower() not in f"{ticker} {company} {form}".lower():
                continue
            records.append(
                SourceRecord(
                    source=SourceType.ANNOUNCEMENTS,
                    date=filing_date,
                    title=f"{company} filed {form}",
                    summary="SEC filing available as of the scan date. Use the filing itself for high-grade issuer evidence.",
                    evidence_grade="high",
                    entities=(ticker.upper(), company),
                    url=_sec_archive_url(cik, accession, doc),
                    metadata={"form": form, "cik": cik, "accession": accession, "primary_document": doc},
                )
            )
            if len(records) >= spec.limit:
                return records
    return records if records else _search_required_records(SourceType.ANNOUNCEMENTS, spec)


def _query_sec_financials(spec: SourceQuerySpec) -> list[SourceRecord]:
    ticker_map = _sec_ticker_map_safe()
    records: list[SourceRecord] = []
    for ticker in _sec_tickers_for_spec(spec):
        cik = ticker_map.get(ticker.upper())
        if not cik:
            continue
        facts = _sec_get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
        company = facts.get("entityName", ticker.upper())
        us_gaap = facts.get("facts", {}).get("us-gaap", {})
        for fact_name in SEC_FACTS:
            fact = us_gaap.get(fact_name)
            if not fact:
                continue
            latest = _latest_fact_unit(fact, spec.date)
            if not latest:
                continue
            value = latest.get("val")
            end = latest.get("end")
            filed = latest.get("filed")
            form = latest.get("form")
            unit = latest.get("unit")
            records.append(
                SourceRecord(
                    source=SourceType.FINANCIALS,
                    date=filed or end or spec.date,
                    title=f"{company} {fact_name}: {_format_number(value)} {unit or ''}".strip(),
                    summary=f"Latest SEC XBRL company fact available by {spec.date}; period end {end}, form {form}.",
                    evidence_grade="high",
                    entities=(ticker.upper(), company, fact_name),
                    url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                    metadata={"cik": cik, "fact": fact_name, "value": value, "unit": unit, "period_end": end, "filed": filed, "form": form},
                )
            )
            if len(records) >= spec.limit:
                return records
    return records if records else _search_required_records(SourceType.FINANCIALS, spec)


def _query_federal_register(spec: SourceQuerySpec) -> list[SourceRecord]:
    term = spec.keyword or " ".join(_entities_for_spec(spec))
    if not term.strip():
        return _search_required_records(SourceType.POLICY, spec)
    params = {
        "conditions[term]": term,
        "conditions[publication_date][lte]": spec.date,
        "per_page": str(min(max(spec.limit, 1), 20)),
        "order": "newest",
    }
    payload = _http_json("https://www.federalregister.gov/api/v1/documents.json?" + urlencode(params))
    records: list[SourceRecord] = []
    for item in payload.get("results", [])[: spec.limit]:
        publication_date = item.get("publication_date") or spec.date
        records.append(
            SourceRecord(
                source=SourceType.POLICY,
                date=publication_date,
                title=item.get("title") or "Federal Register document",
                summary=(item.get("abstract") or item.get("type") or "Official Federal Register document.")[:600],
                evidence_grade="high",
                entities=tuple(item.get("agencies", [{}])[0].get("name", "") for _ in [0]) if item.get("agencies") else (),
                url=item.get("html_url"),
                metadata={"document_number": item.get("document_number"), "type": item.get("type")},
            )
        )
    return records if records else _search_required_records(SourceType.POLICY, spec)


def _fetch_yahoo_daily_record(symbol: str, as_of_date: str, source: SourceType) -> SourceRecord | None:
    target = datetime.fromisoformat(as_of_date).date()
    period1 = int(datetime.combine(target - timedelta(days=10), datetime.min.time(), timezone.utc).timestamp())
    period2 = int(datetime.combine(target + timedelta(days=2), datetime.min.time(), timezone.utc).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol)}?{urlencode({'period1': period1, 'period2': period2, 'interval': '1d', 'events': 'div,splits'})}"
    payload = _http_json(url)
    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result:
        return None
    timestamps = result.get("timestamp") or []
    quote_data = (result.get("indicators", {}).get("quote") or [{}])[0]
    rows: list[tuple[int, str]] = []
    for index, ts in enumerate(timestamps):
        row_date = datetime.fromtimestamp(ts, timezone.utc).date()
        close = _list_get(quote_data.get("close", []), index)
        if row_date <= target and close is not None:
            rows.append((index, row_date.isoformat()))
    if not rows:
        return None
    index, row_date = rows[-1]
    previous_close = None
    if len(rows) >= 2:
        previous_close = _list_get(quote_data.get("close", []), rows[-2][0])
    open_price = _list_get(quote_data.get("open", []), index)
    high = _list_get(quote_data.get("high", []), index)
    low = _list_get(quote_data.get("low", []), index)
    close = _list_get(quote_data.get("close", []), index)
    volume = _list_get(quote_data.get("volume", []), index)
    change_pct = None
    if close is not None and previous_close:
        change_pct = (close / previous_close - 1) * 100
    title = f"{symbol} Yahoo daily bar as of {row_date}"
    summary = f"Open {open_price}, high {high}, low {low}, close {close}, volume {volume}."
    if change_pct is not None:
        summary += f" Day change {change_pct:.2f}% versus prior available close."
    return SourceRecord(
        source=source,
        date=row_date,
        title=title,
        summary=summary,
        evidence_grade="medium",
        entities=(symbol,),
        url=f"https://finance.yahoo.com/quote/{quote(symbol)}",
        metadata={
            "symbol": symbol,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "day_change_pct": change_pct,
            "provider": "Yahoo Finance chart API",
        },
    )


def _search_required_records(source: SourceType, spec: SourceQuerySpec) -> list[SourceRecord]:
    keyword = spec.keyword or " ".join(_entities_for_spec(spec)) or source.value
    targets = _search_targets(source)
    queries = [f"{keyword} {target} as of {spec.date}" for target in targets[:4]]
    return [
        SourceRecord(
            source=source,
            date=spec.date,
            title=f"Search required for {source.value}",
            summary=(
                "No stable unauthenticated adapter is bundled for this source or the live query returned no usable records. "
                "Use web/search tools with the scan date as a hard cutoff; prefer official/primary sources and record failed searches."
            ),
            evidence_grade="search-required",
            entities=_entities_for_spec(spec),
            metadata={"queries": queries, "preferred_targets": targets, "as_of_cutoff": spec.date},
        )
    ]


def _search_targets(source: SourceType) -> tuple[str, ...]:
    return {
        SourceType.ANNOUNCEMENTS: ("official company IR", "SEC EDGAR", "CNINFO 巨潮资讯", "SSE/SZSE exchange filing"),
        SourceType.FINANCIALS: ("SEC companyfacts", "company annual report", "quarterly report", "investor presentation"),
        SourceType.CALLS: ("official earnings call transcript", "investor day transcript", "company IR webcast", "8-K transcript exhibit"),
        SourceType.POLICY: ("official government policy", "White House USTR Federal Register", "SCIO NDRC MIIT official", "tariff export control notice"),
        SourceType.INDUSTRY_PRICING: ("TrendForce DRAMeXchange", "LightCounting", "Omdia", "company pricing commentary"),
        SourceType.GLOBAL_LEADERS: ("official company IR", "SEC filing", "earnings call", "Yahoo Finance tape"),
        SourceType.MARKET: ("Yahoo Finance", "exchange OHLCV", "market cap PE turnover", "relative strength"),
    }[source]


def _symbols_for_spec(spec: SourceQuerySpec) -> tuple[str, ...]:
    symbols: list[str] = []
    for entity in _entities_for_spec(spec):
        normalized = _normalize_symbol(entity)
        if normalized:
            symbols.append(normalized)
    keyword = (spec.keyword or "").lower()
    symbols.extend(_symbols_from_text(keyword))
    for triggers, mapped_symbols in THEME_SYMBOLS:
        if any(trigger in keyword for trigger in triggers):
            symbols.extend(mapped_symbols)
    return _dedupe(symbols)


def _sec_tickers_for_spec(spec: SourceQuerySpec) -> tuple[str, ...]:
    tickers: list[str] = []
    for entity in _entities_for_spec(spec):
        alias = SEC_TICKER_ALIASES.get(entity.lower())
        if alias:
            tickers.append(alias)
            continue
        normalized = _normalize_us_ticker(entity)
        if normalized:
            tickers.append(normalized)
    keyword = (spec.keyword or "").lower()
    for key, ticker in SEC_TICKER_ALIASES.items():
        if key in keyword:
            tickers.append(ticker)
    if any(token in keyword for token in ("memory", "dram", "hbm", "存储", "内存")):
        tickers.append("MU")
    if any(token in keyword for token in ("nvidia", "gpu", "accelerator", "blackwell")):
        tickers.append("NVDA")
    return _dedupe(tickers)


def _entities_for_spec(spec: SourceQuerySpec) -> tuple[str, ...]:
    return tuple(_requested_entities(spec))


def _symbols_from_text(text: str) -> list[str]:
    blocked = {"AI", "DRAM", "HBM", "CPO", "GPT", "LLM", "SEC", "USA", "US"}
    return [match for match in re.findall(r"\b[A-Z]{1,5}(?:\.[A-Z]{1,3})?\b", text.upper()) if match not in blocked]


def _normalize_symbol(entity: str) -> str | None:
    raw = entity.strip()
    if not raw:
        return None
    if re.fullmatch(r"\d{6}\.(SZ|SH)", raw.upper()):
        return raw.upper()
    if re.fullmatch(r"\d{4,6}\.(KS|KQ|HK|T|TW)", raw.upper()):
        return raw.upper()
    if re.fullmatch(r"[A-Za-z]{1,5}(?:\.[A-Za-z]{1,3})?", raw):
        return raw.upper()
    alias = SEC_TICKER_ALIASES.get(raw.lower())
    return alias


def _normalize_us_ticker(entity: str) -> str | None:
    raw = entity.strip().upper()
    if re.fullmatch(r"[A-Z]{1,5}", raw):
        return raw
    return None


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


@lru_cache(maxsize=1)
def _sec_ticker_map() -> dict[str, str]:
    data = _http_json("https://www.sec.gov/files/company_tickers.json", sec=True)
    result: dict[str, str] = {}
    for row in data.values():
        ticker = str(row.get("ticker", "")).upper()
        cik = str(row.get("cik_str", "")).zfill(10)
        if ticker and cik:
            result[ticker] = cik
    return result


def _sec_ticker_map_safe() -> dict[str, str]:
    try:
        return _sec_ticker_map()
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        return {}


def _sec_get_json(url: str) -> dict[str, Any]:
    return _http_json(url, sec=True)


def _http_json(url: str, *, sec: bool = False) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT}
    if sec:
        headers["Accept"] = "application/json"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        return json.load(response)


def _sec_archive_url(cik: str, accession: str, primary_doc: str) -> str:
    cik_int = str(int(cik))
    accession_path = accession.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_path}/{primary_doc}"


def _latest_fact_unit(fact: dict[str, Any], as_of_date: str) -> dict[str, Any] | None:
    units = fact.get("units", {})
    candidates: list[dict[str, Any]] = []
    cutoff = datetime.fromisoformat(as_of_date).date() - timedelta(days=1095)
    for unit, rows in units.items():
        for row in rows:
            filed = row.get("filed") or ""
            end = row.get("end") or ""
            if filed and filed > as_of_date:
                continue
            if end and end > as_of_date:
                continue
            if filed and datetime.fromisoformat(filed).date() < cutoff:
                continue
            if row.get("form") not in {"10-K", "10-Q", "20-F", "40-F"}:
                continue
            enriched = dict(row)
            enriched["unit"] = unit
            candidates.append(enriched)
    if not candidates:
        return None
    candidates.sort(key=lambda row: (row.get("end") or "", row.get("filed") or ""), reverse=True)
    return candidates[0]


def _format_number(value: Any) -> str:
    if isinstance(value, (int, float)):
        abs_value = abs(value)
        if abs_value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        if abs_value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
    return str(value)


def _list_get(values: list[Any], index: int) -> Any:
    try:
        return values[index]
    except (IndexError, TypeError):
        return None


def fixture_records() -> tuple[SourceRecord, ...]:
    return (
        SourceRecord(
            source=SourceType.MARKET,
            date="2023-03-22",
            title="High-purity optical module leader printed early bullish confirmation",
            summary="Fixture market row: high-speed optical module exposure, large daily candle, expanded volume, and strong relative strength after the GPT-4 capability shock.",
            evidence_grade="medium",
            entities=("Zhongji Innolight", "AI optical modules", "GPT-4"),
            metadata={"symbols": ("300308.SZ",), "move_type": "early_large_bullish_candle"},
        ),
        SourceRecord(
            source=SourceType.GLOBAL_LEADERS,
            date="2023-03-22",
            title="Frontier model release increased AI compute and networking expectations",
            summary="Fixture global-leader row: a new frontier LLM release raised perceived AI deployment utility and datacenter infrastructure intensity.",
            evidence_grade="high",
            entities=("GPT-4", "AI datacenter", "accelerators", "networking"),
            metadata={"read_through": "compute_networking_demand"},
        ),
        SourceRecord(
            source=SourceType.INDUSTRY_PRICING,
            date="2023-03-22",
            title="AI datacenter bandwidth demand highlighted high-speed optical module scarcity",
            summary="Fixture industry-pricing row: checks focus on 400G/800G optical module demand, qualification cycles, and limited high-purity supplier set.",
            evidence_grade="medium",
            entities=("400G", "800G", "AI optical modules"),
            metadata={"indicator": "demand_visibility"},
        ),
        SourceRecord(
            source=SourceType.FINANCIALS,
            date="2023-03-22",
            title="Prior filings showed datacenter optical exposure mattered to earnings purity",
            summary="Fixture financial row: segment and customer exposure screen keeps the candidate closer to AI datacenter capex than generic AI software themes.",
            evidence_grade="high",
            entities=("Zhongji Innolight", "datacenter optical modules"),
            metadata={"symbols": ("300308.SZ",), "purity_hint": "datacenter_optical_module"},
        ),
        SourceRecord(
            source=SourceType.MARKET,
            date="2025-05-12",
            title="Overseas memory leader gap-up confirmed risk-on repricing",
            summary="Fixture market row: a globally relevant memory producer opened sharply higher as trade-risk pressure eased and AI memory tightness stayed in focus.",
            evidence_grade="medium",
            entities=("Micron", "DRAM", "HBM", "AI memory"),
            metadata={"symbols": ("MU",), "move_type": "gap_up_strong_close"},
        ),
        SourceRecord(
            source=SourceType.GLOBAL_LEADERS,
            date="2025-05-12",
            title="Memory leader move mapped to AI DRAM and HBM supply-demand tightness",
            summary="Fixture global-leader row: the overseas leader is fundamentally tied to DRAM/HBM pricing, utilization, and AI server memory content.",
            evidence_grade="high",
            entities=("Micron", "DRAM", "HBM", "AI server"),
            metadata={"symbols": ("MU",), "read_through": "ai_memory_supercycle"},
        ),
        SourceRecord(
            source=SourceType.INDUSTRY_PRICING,
            date="2025-05-12",
            title="Advanced memory checks pointed to stronger pricing and utilization",
            summary="Fixture industry-pricing row: advanced memory supply was tight, pricing power improved, and AI server demand raised capacity absorption.",
            evidence_grade="high",
            entities=("DRAM", "HBM", "AI memory"),
            metadata={"indicator": "tight_supply_pricing_power"},
        ),
        SourceRecord(
            source=SourceType.POLICY,
            date="2025-05-12",
            title="Trade-risk easing reduced worst-case supply-chain discount",
            summary="Fixture policy row: tariff and trade-risk headlines reduced perceived downside tail risk for globally exposed semiconductor assets.",
            evidence_grade="medium",
            entities=("trade risk", "tariff", "semiconductors"),
            metadata={"policy_type": "risk_easing"},
        ),
        SourceRecord(
            source=SourceType.MARKET,
            date="2025-05-08",
            title="Core AI optical supply-chain asset rallied from tariff-panic discount",
            summary="Fixture market row: a high-purity optical module supplier printed a large bullish candle after trade-war fear compressed valuation and positioning.",
            evidence_grade="medium",
            entities=("Zhongji Innolight", "AI optical modules", "trade risk"),
            metadata={"symbols": ("300308.SZ",), "move_type": "risk_discount_reversal"},
        ),
        SourceRecord(
            source=SourceType.POLICY,
            date="2025-05-08",
            title="Trade-war fear eased enough to reprice exposed AI supply-chain assets",
            summary="Fixture policy row: the catalyst is not a generic policy theme; it is removal of a risk discount from a still-strong AI infrastructure demand curve.",
            evidence_grade="medium",
            entities=("trade risk", "AI supply chain", "tariff"),
            metadata={"policy_type": "risk_discount_removal"},
        ),
        SourceRecord(
            source=SourceType.FINANCIALS,
            date="2025-05-08",
            title="High-purity optical module exposure supported core-asset classification",
            summary="Fixture financial row: disclosed product exposure keeps the asset in the core AI datacenter supply chain rather than a low-purity rebound basket.",
            evidence_grade="high",
            entities=("Zhongji Innolight", "AI datacenter", "optical modules"),
            metadata={"symbols": ("300308.SZ",), "purity_hint": "core_ai_supply_chain"},
        ),
        SourceRecord(
            source=SourceType.CALLS,
            date="2025-05-08",
            title="Industry commentary kept AI datacenter demand curve intact",
            summary="Fixture call row: management and industry commentary before the risk-panic episode did not disprove the AI infrastructure demand trend.",
            evidence_grade="high",
            entities=("AI datacenter", "optical modules", "cloud capex"),
            metadata={"signal": "demand_curve_not_broken"},
        ),
        SourceRecord(
            source=SourceType.ANNOUNCEMENTS,
            date="2026-01-01",
            title="Fixture placeholder for issuer announcements",
            summary="Replace this row with exchange filings, company announcements, order disclosures, and timestamped issuer notices.",
            evidence_grade="high",
            entities=("fixture",),
            metadata={"todo": "connect issuer filing adapter"},
        ),
        SourceRecord(
            source=SourceType.CALLS,
            date="2026-01-01",
            title="Fixture placeholder for call transcripts",
            summary="Replace this row with earnings-call, investor-day, conference-call, and expert-call transcript adapters.",
            evidence_grade="high",
            entities=("fixture",),
            metadata={"todo": "connect transcript adapter"},
        ),
    )


def _requested_entities(spec: SourceQuerySpec) -> set[str]:
    values: list[str] = []
    for attr in ("symbols", "issuers", "companies", "jurisdictions", "commodities"):
        values.extend(getattr(spec, attr, ()) or ())
    return {value.lower() for value in values if value}


def _search_blob(record: SourceRecord) -> str:
    return " ".join(
        [
            record.title,
            record.summary,
            " ".join(record.entities),
            json.dumps(record.metadata, ensure_ascii=False, sort_keys=True),
        ]
    ).lower()


def _keyword_matches(keyword: str, blob: str) -> bool:
    if keyword in blob:
        return True
    tokens = re.findall(r"[a-z0-9_.+-]+", keyword)
    return bool(tokens) and all(token in blob for token in tokens)


def _render_record(record: SourceRecord) -> list[str]:
    lines = [
        f"- [{record.evidence_grade}] {record.date} - {record.title}",
        f"  Summary: {record.summary}",
    ]
    if record.entities:
        lines.append(f"  Entities: {', '.join(record.entities)}")
    if record.url:
        lines.append(f"  URL: {record.url}")
    if record.metadata:
        metadata = json.dumps(record.metadata, ensure_ascii=False, sort_keys=True)
        lines.append(f"  Metadata: {metadata}")
    lines.append("")
    return lines
