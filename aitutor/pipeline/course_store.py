"""Persist LLM-built course JSON and load it for tutor/lecture."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aitutor.pipeline.provenance import attach_provenance


def built_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "content" / "courses" / "built"


_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def extract_course_json(text: str) -> dict[str, Any]:
    text = text.strip()
    m = _JSON_FENCE.search(text)
    if m:
        return json.loads(m.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON object found in builder output")


def _slug(course_id: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", course_id.strip()).strip("-").lower()
    return s or "untitled"


@dataclass
class StoredCourse:
    path: Path
    data: dict[str, Any]

    @property
    def course_id(self) -> str:
        return str(self.data.get("course_id") or self.path.stem)


def save_course(
    data: dict[str, Any],
    *,
    directory: Path | None = None,
    with_whi: bool = True,
) -> StoredCourse:
    required = ("course_id", "title", "weeks")
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Course JSON missing keys: {missing}")
    if not isinstance(data["weeks"], list) or not data["weeks"]:
        raise ValueError("Course JSON weeks must be a non-empty list")

    data = attach_provenance(dict(data), with_whi=with_whi)
    d = directory or built_dir()
    d.mkdir(parents=True, exist_ok=True)
    cid = _slug(str(data["course_id"]))
    data["course_id"] = cid
    # re-hash after slug normalize
    data = attach_provenance(data, with_whi=with_whi)
    path = d / f"{cid}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return StoredCourse(path=path, data=data)


def save_from_llm_text(
    text: str, *, directory: Path | None = None, with_whi: bool = True
) -> StoredCourse:
    return save_course(extract_course_json(text), directory=directory, with_whi=with_whi)


def load_course(course_id: str, *, directory: Path | None = None) -> StoredCourse:
    d = directory or built_dir()
    path = d / f"{_slug(course_id)}.json"
    if not path.is_file():
        alt = d / f"{course_id}.json"
        path = alt if alt.is_file() else path
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return StoredCourse(path=path, data=data)


def list_built(*, directory: Path | None = None) -> list[StoredCourse]:
    d = directory or built_dir()
    if not d.is_dir():
        return []
    out: list[StoredCourse] = []
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            out.append(StoredCourse(path=p, data=data))
        except (json.JSONDecodeError, OSError):
            continue
    return out