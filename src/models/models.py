import dataclasses
from datetime import datetime

@dataclasses.dataclass
class User:
    user_id: int
    group_id: int
    group_name: str
    sub_group: int
    is_premium: bool

@dataclasses.dataclass
class Group:
    group_id: int
    group_name: str

@dataclasses.dataclass
class Lesson:
    discipline: str
    kind_of_work: str
    auditorium: str
    date: datetime
    beginLesson: datetime
    endLesson: datetime
    lecturer_title: str
    lecturer_rank: str
    sub_group: int
    group_id: int
    id: int = None
