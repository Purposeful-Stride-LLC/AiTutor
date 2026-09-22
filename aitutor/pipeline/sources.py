"""Provenance registry — citations travel with every built course."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from aitutor.pipeline.ingest import IngestedMaterial


@dataclass
class SourceRecord:
    id: str
    title: str
    locator: str
    authority: str
    note: str = ""


@dataclass
class SourceRegistry:
    records: list[SourceRecord] = field(default_factory=list)

    def add_material(self, mat: IngestedMaterial, note: str = "") -> SourceRecord:
        # Stable S1, S2, … for prompt readability
        sid = f"S{len(self.records) + 1}"
        rec = SourceRecord(
            id=sid,
            title=mat.title,
            locator=mat.locator,
            authority=mat.authority_hint,
            note=note or mat.kind,
        )
        self.records.append(rec)
        return rec

    def as_prompt_block(self) -> str:
        lines = ["Sources (cite by id):"]
        for r in self.records:
            lines.append(
                f"- {r.id}: {r.title} [{r.authority}] locator={r.locator} ({r.note})"
            )
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps([asdict(r) for r in self.records], indent=2)

    def save(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")


def default_source_roots_file() -> Path:
    return (
        Path(__file__).resolve().parent.parent.parent
        / "content"
        / "source_roots"
        / "roots.json"
    )


def load_source_roots(path: Path | None = None) -> list[dict]:
    p = path or default_source_roots_file()
    if not p.is_file():
        return []
    return json.loads(p.read_text(encoding="utf-8"))