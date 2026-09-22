"""Bring raw materials into AiTutor without copying giant corpora."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IngestedMaterial:
    material_id: str
    title: str
    locator: str
    kind: str  # file | paste | url | shard
    text: str
    authority_hint: str = "secondary"  # primary|secondary
    meta: dict = field(default_factory=dict)

    @property
    def excerpt(self) -> str:
        return self.text[:6000]


def _sid(locator: str) -> str:
    h = hashlib.sha1(locator.encode("utf-8", errors="replace")).hexdigest()[:10]
    return f"M-{h}"


def ingest_text(
    text: str,
    *,
    title: str = "parent-syllabus",
    authority_hint: str = "primary",
    kind: str = "paste",
) -> IngestedMaterial:
    locator = f"paste://{title}"
    return IngestedMaterial(
        material_id=_sid(locator),
        title=title,
        locator=locator,
        kind=kind,
        text=text,
        authority_hint=authority_hint,
        meta={"chars": len(text)},
    )


def ingest_path(
    path: Path | str,
    *,
    max_chars: int = 120_000,
    authority_hint: str | None = None,
) -> IngestedMaterial:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    raw = p.read_text(encoding="utf-8", errors="replace")
    if len(raw) > max_chars:
        raw = raw[:max_chars] + "\n\n[truncated for token budget]\n"
    hint = authority_hint or _guess_authority(p)
    return IngestedMaterial(
        material_id=_sid(str(p)),
        title=p.stem,
        locator=str(p),
        kind="file",
        text=raw,
        authority_hint=hint,
        meta={"suffix": p.suffix, "bytes": p.stat().st_size},
    )


def ingest_paths(paths: list[Path | str], **kwargs) -> list[IngestedMaterial]:
    return [ingest_path(p, **kwargs) for p in paths]


_PRIMARY_NAME = re.compile(
    r"(?i)(syllabus|standard|fm[\s_-]?\d|manual|nasa|doe|curriculum|regulation)"
)


def _guess_authority(path: Path) -> str:
    blob = f"{path.name} {path.parent.name}"
    if _PRIMARY_NAME.search(blob):
        return "primary"
    if path.suffix.lower() in {".pdf", ".txt", ".odt"} and "manual" in blob.lower():
        return "primary"
    return "secondary"