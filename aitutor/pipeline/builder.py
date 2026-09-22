"""Assemble the prompt pack that makes an LLM *build* a cited course."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from aitutor.pipeline.ingest import IngestedMaterial
from aitutor.pipeline.sources import SourceRegistry


def _prompts_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "prompts"


def load_builder_methodology() -> str:
    path = _prompts_dir() / "course_builder.md"
    return path.read_text(encoding="utf-8")


@dataclass
class BuildRequest:
    subject: str
    learner: str = "adult professional"
    goal: str = "increase practical self-sufficiency"
    audience: str = "adult"
    materials: list[IngestedMaterial] = field(default_factory=list)
    extra_notes: str = ""


def build_prompt_pack(req: BuildRequest) -> dict:
    """
    Returns a host-ready pack:
      system  — methodology
      user    — subject + learner + source list + excerpts
      registry — SourceRegistry JSON companion
    The host LLM should answer with the course JSON schema from the methodology.
    """
    registry = SourceRegistry()
    excerpt_blocks: list[str] = []
    for mat in req.materials:
        rec = registry.add_material(mat)
        excerpt_blocks.append(
            f"### [{rec.id}] {mat.title}\n"
            f"locator: {mat.locator}\n"
            f"authority: {mat.authority_hint}\n\n"
            f"{mat.excerpt}\n"
        )

    system = load_builder_methodology()
    user_parts = [
        f"Subject: {req.subject}",
        f"Learner: {req.learner}",
        f"Audience: {req.audience}",
        f"Goal: {req.goal}",
        "",
        registry.as_prompt_block(),
        "",
        "Material excerpts:",
        *excerpt_blocks,
    ]
    if req.extra_notes:
        user_parts.extend(["", "Builder notes from human:", req.extra_notes])
    user_parts.append(
        "\nBuild the cited course JSON now. If sources are insufficient, fill gaps[] "
        "and still produce the best honest schedule you can without inventing manuals."
    )

    return {
        "phase": "build",
        "system": system,
        "user": "\n".join(user_parts),
        "sources": json.loads(registry.to_json()),
        "expect": "course_json",
    }