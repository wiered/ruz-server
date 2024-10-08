"""This is models module.

This module contains models.
"""

__all__ = ["User", "Group", "LessonWEB", "LessonDB"]
__version__ = "1.0"
__author__ = "Wiered"

import dataclasses
from datetime import datetime

@dataclasses.dataclass
class User:
    id: int
    group_id: int = 0
    group_name: str = ""
    sub_group: int = 0
    is_premium: bool = False

    def json(self):
        return dataclasses.asdict(self)

@dataclasses.dataclass
class Group:
    group_id: int
    group_name: str

    def json(self):
        return dataclasses.asdict(self)

@dataclasses.dataclass
class LessonWEB:
    discipline: str
    kind_of_work: str
    auditorium: str
    date: str
    beginLesson: str
    endLesson: str
    lecturer_title: str
    lecturer_rank: str
    sub_group: int
    group_id: int

    def json(self):
        return dataclasses.asdict(self)

@dataclasses.dataclass
class LessonDB:
    discipline: str
    kind_of_work: str
    auditorium: str
    date: str
    beginLesson: str
    endLesson: str
    lecturer_title: str
    lecturer_rank: str
    sub_group: int
    group_id: int
    id: int = None

    def json(self):
        return dataclasses.asdict(self)
