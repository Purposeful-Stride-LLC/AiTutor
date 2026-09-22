# AiTutor architecture

## Goal

Raise a human learner’s self-sufficiency and survival odds by turning **raw knowledge**
(manuals, syllabi, state standards, conversation shards, PDFs, notes) into a **cited course**,
then **tutoring / lecturing** that course with an LLM host (Grok-style builder, NOVA as lecturer).

This is not a pile of static lesson files. The product is the **recursive methodology**:

```
subject or raw materials
        │
        ▼
   INGEST  ──► normalize files / parent paste / state DOE pull / web allowlist
        │
        ▼
   SOURCE  ──► rank authoritative materials, keep provenance
        │
        ▼
   BUILD   ──► LLM builds syllabus + weeks + activities (cite every claim)
        │
        ▼
   TUTOR   ──► human session against the built plan (Socratic / activity-first)
        │
        ▼
   LECTURE ─► optional NOVA voice/GUI delivery of the same plan
```

## Why this matches the Grok conversations

In the thumb HTML threads (Professor Prompt Design, NASA Modeling, FreeCAD two-week course, …)
the pattern repeats:

1. Human names a domain or pastes a seed (“structural geology on the Moon”, “NASA APIs”, …).
2. Model **assumes professor role** and **pulls a class schedule out of the conversation**
   (weeks, objectives, activities) — that extraction *is* course construction.
3. Teaching continues from that schedule, with personalization (transcript / prior skills).
4. Continuity shards (ZeroFrame-style) let another instance pick up without dementia reset.

AiTutor freezes that loop as code + prompt contracts so NOVA (or any host) can run it offline.

## Flexibility (inputs)

| Input kind | Example | Handler |
|------------|---------|---------|
| Distilled courses | `content/courses/*.txt` (AD_ASTRA) | `catalog` |
| Local corpus | Military FM, FreeCAD notes, beekeeping, digestion manuals under `D:\pg\documents` | `ingest` + `source_roots` |
| Parent K–12 | Pasted district syllabus / weekly outline | `ingest.from_text` |
| State / DOE | Standards PDF or URL (when online) | `ingest.from_url` (optional) |
| Conversation shard | Professor / course HTML or ZeroFrame summary | `ingest.from_shard` |

Diversification is intentional: sausage grinders and FM 3-19.17 sit beside NASA modeling.
Survival skills and collegiate STEM use the **same pipeline**.

## Modules

| Package path | Role |
|--------------|------|
| `aitutor.catalog` | Indexed baked courses |
| `aitutor.lesson` | Parse syllabus → week units |
| `aitutor.professor` | Tutor persona |
| `aitutor.session` | Human turn log + prompt bundle |
| `aitutor.pipeline.ingest` | Bring raw materials in |
| `aitutor.pipeline.sources` | Provenance + citation records |
| `aitutor.pipeline.builder` | Prompt pack that asks the LLM to **build** a course |
| `aitutor.pipeline.lecture` | Thin NOVA lecture adapter |
| `aitutor.prompts` | Reusable methodology prompts |
| `aitutor.nova_bridge` | Optional plug into NOVA without bloating fieldkit |

## Citation rule (hard)

Every built week must carry `sources[]` with at least: title, locator (path/URL),
and a short “why authoritative” note. The tutor may not invent standards, regs, or
NASA/DoD credentials. If the corpus is thin, the builder says so and asks for more material.

## Host split

- **Builder host** (Grok / strong model): ingest → source → build syllabus JSON.
- **Tutor host** (same or local): session turns against the built plan.
- **Lecturer** (NOVA): speak/present units; does not own the corpus.

Keep the corpus in Projects/`AiTutor` (or pointed `source_roots`), never copied wholesale into fieldkit.

## Provenance (NOVA paper shape)

Built courses under `content/courses/built/*.json` carry:
- `sources[].sha256` — content hash of each cited file when on disk
- `provenance.content_sha256` — hash of the course body (cite+structure)
- optional `WHI` header (`0x-DOC`) with cite ids for later NOVA ingest

Attached automatically by `save_course` / `import-course`. No fat DB join.