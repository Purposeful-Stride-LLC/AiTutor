"""CLI: python -m aitutor …"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aitutor.catalog import CourseCatalog
from aitutor.lesson import parse_lesson_plan
from aitutor.nova_bridge import TutorModule
from aitutor.pipeline.builder import BuildRequest, build_prompt_pack
from aitutor.pipeline.course_store import list_built, save_from_llm_text
from aitutor.pipeline.ingest import ingest_path, ingest_text
from aitutor.pipeline.lecture import lecture_payload
from aitutor.pipeline.sources import load_source_roots
from aitutor.session import TutorSession


def cmd_list(_: argparse.Namespace) -> int:
    for c in CourseCatalog().list():
        tags = ",".join(c.tags)
        print(f"{c.course_id:32}  {c.kind:5}  {c.title}  [{c.audience}]  {tags}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    plan = parse_lesson_plan(args.course_id)
    print(f"# {plan.course.title}")
    print(plan.overview[:500] or "(no overview parsed)")
    print()
    for w in plan.weeks:
        print(f"  Week {w.week}: {w.title}")
        if w.objective:
            print(f"    Objective: {w.objective}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    session = TutorSession.start(args.course_id, week=args.week)
    print(session.last_tutor())
    print()
    print("--- prompt bundle (for host LLM) ---")
    print(json.dumps(session.prompt_bundle(), indent=2)[:2000])
    return 0


def cmd_session(args: argparse.Namespace) -> int:
    session = TutorSession.start(
        args.course_id, week=args.week, learner_name=args.name or "learner"
    )
    print(session.last_tutor())
    print("(type a reply, or /week N, /prompt, /quit)")
    while True:
        try:
            line = input(f"{session.learner_name}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line in {"/quit", "/exit", "quit", "exit"}:
            break
        if line.startswith("/week"):
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                print("usage: /week 1")
                continue
            print(session.set_week(parts[1].strip()))
            continue
        if line == "/prompt":
            print(json.dumps(session.prompt_bundle(), indent=2)[:3000])
            continue
        session.human_say(line)
        reply = (
            f"[AiTutor offline stub] Noted. Feed `prompt_bundle()` to your LLM host "
            f"(NOVA / OpenClaw / local). You said: {line[:200]}"
        )
        print(session.tutor_say(reply))
    return 0


def cmd_manifest(_: argparse.Namespace) -> int:
    print(json.dumps(TutorModule().nova_manifest(), indent=2))
    return 0


def cmd_roots(_: argparse.Namespace) -> int:
    print(json.dumps(load_source_roots(), indent=2))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    materials = []
    for path in args.file or []:
        materials.append(ingest_path(path))
    if args.paste:
        paste = Path(args.paste).read_text(encoding="utf-8", errors="replace")
        materials.append(
            ingest_text(
                paste,
                title=args.paste_title or "parent-syllabus",
                authority_hint="primary",
            )
        )
    if args.stdin_paste:
        materials.append(
            ingest_text(sys.stdin.read(), title="stdin-syllabus", authority_hint="primary")
        )
    if not materials and not args.subject:
        print(
            "Need --subject and at least one --file / --paste / --stdin-paste",
            file=sys.stderr,
        )
        return 2
    req = BuildRequest(
        subject=args.subject or (materials[0].title if materials else "untitled"),
        learner=args.learner,
        goal=args.goal,
        audience=args.audience,
        materials=materials,
        extra_notes=args.notes or "",
    )
    pack = build_prompt_pack(req)
    out = args.out
    text = json.dumps(pack, indent=2)
    if out:
        Path(out).write_text(text, encoding="utf-8")
        print(f"wrote build prompt pack -> {out}")
    else:
        print(
            json.dumps(
                {
                    "phase": pack["phase"],
                    "expect": pack["expect"],
                    "sources": pack["sources"],
                    "system_chars": len(pack["system"]),
                    "user_chars": len(pack["user"]),
                    "user_preview": pack["user"][:1500],
                },
                indent=2,
            )
        )
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()
    stored = save_from_llm_text(text)
    print(f"saved {stored.course_id} -> {stored.path}")
    return 0


def cmd_built(_: argparse.Namespace) -> int:
    for s in list_built():
        print(f"{s.course_id:32}  {s.path}")
    return 0


def cmd_lecture(args: argparse.Namespace) -> int:
    plan = parse_lesson_plan(args.course_id)
    payload = lecture_payload(plan, week=args.week)
    print(json.dumps(payload, indent=2)[:4000])
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="aitutor", description="AiTutor education module")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="List baked + built course ids")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="Show parsed lesson plan")
    s.add_argument("course_id")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("start", help="Open a session and print opening + prompt bundle")
    s.add_argument("course_id")
    s.add_argument("--week", default=None)
    s.set_defaults(func=cmd_start)

    s = sub.add_parser("session", help="Interactive REPL (offline stub replies)")
    s.add_argument("course_id")
    s.add_argument("--week", default=None)
    s.add_argument("--name", default="learner")
    s.set_defaults(func=cmd_session)

    s = sub.add_parser("manifest", help="NOVA module manifest JSON")
    s.set_defaults(func=cmd_manifest)

    s = sub.add_parser("roots", help="Show configured local source roots")
    s.set_defaults(func=cmd_roots)

    s = sub.add_parser(
        "build",
        help="Assemble course-builder prompt pack from subject + raw materials",
    )
    s.add_argument("--subject", default=None)
    s.add_argument("--learner", default="adult professional")
    s.add_argument("--goal", default="increase practical self-sufficiency")
    s.add_argument("--audience", default="adult", choices=["adult", "child", "mixed"])
    s.add_argument("--file", action="append", default=[])
    s.add_argument("--paste", default=None)
    s.add_argument("--paste-title", default=None)
    s.add_argument("--stdin-paste", action="store_true")
    s.add_argument("--notes", default=None)
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_build)

    s = sub.add_parser(
        "import-course",
        help="Save builder LLM JSON (file or stdin) into content/courses/built/",
    )
    s.add_argument("--file", default=None)
    s.set_defaults(func=cmd_import)

    s = sub.add_parser("built", help="List LLM-built courses on disk")
    s.set_defaults(func=cmd_built)

    s = sub.add_parser("lecture", help="NOVA lecture payload for a baked or built course week")
    s.add_argument("course_id")
    s.add_argument("--week", default=None)
    s.set_defaults(func=cmd_lecture)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())