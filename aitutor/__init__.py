"""AiTutor — lean education module for Ad Astra / NOVA."""

from aitutor.catalog import CourseCatalog, list_courses
from aitutor.lesson import LessonPlan, WeekUnit
from aitutor.session import TutorSession

__version__ = "0.1.0"
__all__ = [
    "CourseCatalog",
    "LessonPlan",
    "TutorSession",
    "WeekUnit",
    "list_courses",
    "__version__",
]
