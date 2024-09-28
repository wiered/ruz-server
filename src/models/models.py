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

    def json(self):
        return dataclasses.asdict(self)
