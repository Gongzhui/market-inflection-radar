from dataclasses import dataclass
from typing import Protocol

from .gates import Candidate


@dataclass(frozen=True)
class ScanContext:
    date: str
    theme: str | None = None


class DataAdapter(Protocol):
    def collect_candidates(self, context: ScanContext) -> list[Candidate]:
        """Return candidates ready for seven-gate assessment."""


class NullDataAdapter:
    def collect_candidates(self, context: ScanContext) -> list[Candidate]:
        return []
