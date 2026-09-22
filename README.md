## Audit

**Strengths**
- Clear product idea: ingest raw material → sourced course → tutor/lecture.
- Layout and CLI examples exist.
- Integration boundary with NOVA is useful.

**Problems**
- Voice is insider slang (`Grok threads`, `thumb corpora`, `Brand lineage`, `Professor Grok`) rather than project documentation.
- Audience is undefined. A README should say what the tool is, who it is for, and what “done” looks like.
- Commands assume a single Windows path (`C:\Users\wuchy\...`) and mix `set PYTHONPATH=.` with Unix-looking layout. That is not portable.
- Broken markup: `` `ash ``, unclosed code fences, mixed slash styles.
- “Recursive methodology” is a pipeline, not recursion. Name the pipeline accurately.
- Missing sections: requirements, install, command reference, config, data ownership, limitations, license/status.
- “Diversified on purpose — NASA modeling and military working-dog FMs” is a claim without explaining *why* that matters to a reader.
- `content/source_roots/` “pointers, not vendored” needs one sentence on what operators must supply.
- Name/brand paragraph does not belong near the top of a technical README.

---

## Rewritten README

```markdown
# AiTutor

AiTutor is a standalone education module for the Ad Astra / NOVA stack.

It turns raw source material — field manuals, syllabi, standards, notes, and
conversation exports — into a cited course outline, then runs that course as a
tutoring session or a NOVA lecture payload.

The same pipeline is used for dissimilar domains (for example aerospace modeling
and military working-dog fundamentals) so course construction stays consistent
across subjects.

## What it does

1. **Ingest** source files, pasted text, or an optional standards URL.
2. **Source** each item with provenance and authority tags.
3. **Build** a class schedule and lesson structure from those sources.
4. **Tutor** the resulting course in a human session.
5. **Lecture** optionally emits a NOVA delivery payload.

Design notes: `docs/ARCHITECTURE.md`  
Builder prompts: `aitutor/prompts/course_builder.md`

AiTutor owns the corpus and the methodology. NOVA delivers lectures. Do not
fold course content into fieldkit.

## Repository layout

```text
AiTutor/
  aitutor/                 Python package
    pipeline/              ingest, sourcing, builder, lecture
    prompts/               builder and tutor prompts
  content/courses/         distilled course syllabi
  content/courses/built/   courses imported after an LLM build
  content/source_roots/    pointers to external source corpora (not vendored)
  content/shards/          maps back to conversation exports
  docs/ARCHITECTURE.md
```

`content/source_roots/` stores references to corpora that live outside this
repository. Those files must be present on the host before a build that
depends on them.

## Requirements

- Python 3.10+ recommended
- Project root on `PYTHONPATH`
- Access to a host LLM when building a new course (Grok, NOVA, or a local model)

## Setup

From the repository root:

```bash
# Windows
set PYTHONPATH=.

# macOS / Linux
export PYTHONPATH=.
```

Install any project extras from the package’s usual install path when one is
provided. Until then, run the module from the repo root as shown below.

## Quick start

List available courses:

```bash
python -m aitutor list
```

Start an existing course:

```bash
python -m aitutor start geology-aerospace --week 1
```

Inspect configured source roots:

```bash
python -m aitutor roots
```

Emit a NOVA lecture payload:

```bash
python -m aitutor lecture nasa-modeling --week 1
```

## Build a new course

Building is a three-step process. AiTutor assembles a prompt pack; a host LLM
writes the course JSON; AiTutor imports that JSON.

### 1. Assemble a prompt pack

From a file:

```bash
python -m aitutor build \
  --subject "Military Working Dog basics" \
  --audience adult \
  --goal "competent K9 handler fundamentals" \
  --file path/to/MilitaryWorkingDogFM3-19_17.txt \
  --out build_pack.json
```

From a pasted K-12 syllabus:

```bash
python -m aitutor build \
  --subject "Grade 5 science" \
  --audience child \
  --paste path/to/district_syllabus.txt \
  --out k12_pack.json
```

### 2. Run the pack through a host model

Send `build_pack.json` (or `k12_pack.json`) to Grok, NOVA, or a local model and
save the model’s course JSON.

### 3. Import and use the course

```bash
python -m aitutor import-course --file course_from_llm.json
python -m aitutor list
python -m aitutor start military-working-dog-fm3-19-17 --week 1
python -m aitutor lecture military-working-dog-fm3-19-17 --week 1
```

Imported courses are written to `content/courses/built/`.

## NOVA integration

AiTutor exposes a thin bridge. NOVA should consume lesson plans; it should not
own source corpora.

```python
from aitutor.nova_bridge import TutorModule

mod = TutorModule.from_content_dir()
plan = mod.lesson_plan("nasa-modeling")
```

## Command summary

| Command | Purpose |
| --- | --- |
| `python -m aitutor list` | List imported and packaged courses |
| `python -m aitutor start <course> --week N` | Open a tutoring session |
| `python -m aitutor build ... --out pack.json` | Emit an LLM prompt pack |
| `python -m aitutor import-course --file course.json` | Import a built course |
| `python -m aitutor lecture <course> --week N` | Emit a NOVA lecture payload |
| `python -m aitutor roots` | Show configured source-root pointers |

## Naming

- Repository / folder: `AiTutor`
- Python package: `aitutor`
- Related stack: Ad Astra / NOVA

## Status

This module is intended to run standalone. Course quality depends on the
authority of the ingested sources and on the host model used during build.
Always retain original citations in imported course JSON.
```

That version reads like a project file instead of a lab note. If you want a still-tighter variant, the next cut would drop the naming section entirely and add a one-page CLI flag reference from the actual parser.
++++++++++++++++++++

# AiTutor

Standalone **education module** for the Ad Astra / NOVA stack.

**Goal:** raise human self-sufficiency by turning raw knowledge (manuals, syllabi,
state standards, conversation shards) into a **cited course**, then tutoring or
lecturing it. Diversified on purpose — NASA modeling and military working-dog FMs
use the same pipeline.

## The recursive methodology (the product)

```
subject / raw materials
   → INGEST (file, parent paste, optional DOE URL)
   → SOURCE (provenance + authority tags)
   → BUILD  (LLM pulls a class schedule out — like the Grok threads)
   → TUTOR  (human session)
   → LECTURE (optional NOVA delivery)
```

See `docs/ARCHITECTURE.md` and `aitutor/prompts/course_builder.md`.

## Layout

```
AiTutor/
  aitutor/              package
    pipeline/           ingest, sources, builder, lecture
    prompts/            methodology prompts
  content/courses/      distilled AD_ASTRA syllabi
  content/source_roots/ pointers to thumb corpora (not vendored)
  content/shards/       map back to Grok HTML conversations
  docs/ARCHITECTURE.md
```

## Quick start

```bash
cd C:\Users\wuchy\Projects\AiTutor
set PYTHONPATH=.

python -m aitutor list
python -m aitutor start geology-aerospace --week 1

# Build a NEW course from raw materials (emits host LLM prompt pack)
python -m aitutor build --subject "Military Working Dog basics" --audience adult --goal "competent K9 handler fundamentals" --file "D:\pg\documents\fm3_19_17MWDog\MilitaryWorkingDogFM3-19_17.txt" --out build_pack.json

# Parent K-12 syllabus paste
python -m aitutor build --subject "Grade 5 science" --audience child --paste path\to\district_syllabus.txt --out k12_pack.json

# NOVA lecture payload
python -m aitutor lecture nasa-modeling --week 1
python -m aitutor roots
```

## NOVA integration (thin)

```python
from aitutor.nova_bridge import TutorModule
mod = TutorModule.from_content_dir()
plan = mod.lesson_plan("nasa-modeling")
```

NOVA lectures; AiTutor owns corpus + methodology. Do not fold courses into fieldkit.

## Name

Folder/package: `AiTutor` / `aitutor`. Brand lineage: Ad Astra · GZU · Professor Grok.

## Built courses (after LLM build)

`ash
# 1) Assemble prompt pack for host LLM
python -m aitutor build --subject "..." --file path\to\manual.txt --out pack.json

# 2) Run pack through Grok/NOVA/local model → course JSON

# 3) Import result
python -m aitutor import-course --file course_from_llm.json
python -m aitutor list
python -m aitutor start military-working-dog-fm3-19-17 --week 1
python -m aitutor lecture military-working-dog-fm3-19-17 --week 1
`

Built JSON lands in `content/courses/built/`.