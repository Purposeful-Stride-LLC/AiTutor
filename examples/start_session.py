# Example: start a geology→aerospace session from another process / NOVA

from aitutor.nova_bridge import TutorModule

mod = TutorModule.from_content_dir()
print("Courses:", [c["id"] for c in mod.list_courses()])

session = mod.start_session("geology-aerospace", week=1, learner_name="Michael")
print(session.last_tutor())
# Hand session.prompt_bundle() to your LLM host.
