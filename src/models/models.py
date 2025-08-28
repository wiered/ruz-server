import datetime
from datetime import timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import (BigInteger, CheckConstraint, Date, ForeignKey,
                        Integer, Numeric, String, Time)
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlmodel import Column, Field, Relationship, SQLModel, UniqueConstraint


class LessonGroup(SQLModel, table=True):
    """Chains lessons to groups"""
    __tablename__ = "lesson_group"
    lesson_id: int = Field(
        sa_column=Column(
            ForeignKey("lesson.id", ondelete="CASCADE"),
            primary_key=True
        )
    ) # lessonOid
    group_id: int = Field(
        sa_column=Column(
            ForeignKey("groups.id", ondelete="CASCADE"),
            primary_key=True
        )
    ) # groupOid


class Group(SQLModel, table=True):
    __tablename__ = "groups"
    id: int = Field(default=None, primary_key=True) # groupOid
    guid: UUID = Field(
        default=None,
        nullable=False,
        sa_type=SA_UUID(as_uuid=True)
        ) # groupGUID
    name: str = Field(sa_column=Column(
        "name",
        String,
        nullable=False,
        unique=True
    ))
    faculty_name: str = Field(sa_column=Column(
        "faculty_name",
        String,
        nullable=False
    ))

    users: List["User"] = Relationship(back_populates="group")
    lessons: List["Lesson"] = Relationship(
        link_model=LessonGroup
    )


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(
        sa_column=Column(
            "id",
            BigInteger,
            primary_key=True
        )
    ) # telegram id
    group_oid: int = Field(
        sa_column=Column(
            ForeignKey("groups.id", ondelete="SET NULL"),
            nullable=True
        )
    )
    subgroup: int = Field(default=0)
    username: str = Field(sa_column=Column(
        "username",
        String,
        nullable=False
    ))
    created_at: datetime.datetime = Field(default=datetime.datetime.now(timezone.utc))
    last_used_at: datetime.datetime = Field(default=datetime.datetime.now(timezone.utc))

    group: Optional[Group] = Relationship(back_populates="users")


class Lecturer(SQLModel, table=True):
    __tablename__ = "lecturer"
    id: int = Field(default=None, primary_key=True) # lecturerOid
    guid: UUID = Field(
        default=None,
        nullable=False,
        sa_type=SA_UUID(as_uuid=True)
        ) # lecturerGUID
    full_name: str = Field(sa_column=Column(
        "full_name",
        String,
        nullable=False
    ))
    short_name: str = Field(sa_column=Column(
        "short_name",
        String,
        nullable=False
    ))
    rank: str = Field(sa_column=Column(
        "rank",
        String,
        nullable=False
    ))

    lessons: List["Lesson"] = Relationship(back_populates="lecturer")


class KindOfWork(SQLModel, table=True):
    __tablename__ = "kind_of_work"
    id: int = Field(default=None, primary_key=True) # kindOfWorkOid
    type_of_work: str = Field(sa_column=Column(
        "type_of_work",
        String,
        nullable=False
    ))
    complexity: int = Field(sa_column=Column(
        "complexity",
        Integer,
        nullable=False
    ))

    lessons: List["Lesson"] = Relationship(back_populates="kind_of_work")


class Discipline(SQLModel, table=True):
    __tablename__ = "discipline"
    id: int = Field(default=None, primary_key=True) # disciplineOid
    name: str = Field(sa_column=Column(
        "name",
        String,
        nullable=False
    ))
    examtype: str = Field(sa_column=Column(
        "examtype",
        String
    ))
    has_labs: bool = Field(default=False)

    lessons: List["Lesson"] = Relationship(back_populates="discipline")


class Auditorium(SQLModel, table=True):
    __tablename__ = "auditorium"
    id: int = Field(default=None, primary_key=True) # auditoriumOid
    guid: UUID = Field(
        default=None,
        nullable=False,
        sa_type=SA_UUID(as_uuid=True)
        ) # auditoriumGUID
    name: str = Field(sa_column=Column(
        "name",
        String,
        nullable=False
    ))
    building: str = Field(sa_column=Column(
        "building",
        String,
        nullable=False
    ))

    lessons: List["Lesson"] = Relationship(back_populates="auditorium")


class Lesson(SQLModel, table=True):
    __tablename__ = "lesson"
    id: int = Field(default=None, primary_key=True) # lessonOid
    kind_of_work_id: int = Field(
        sa_column=Column(
            ForeignKey("kind_of_work.id", ondelete="CASCADE")
        ) # kindOfWorkOid
    )
    discipline_id: int = Field(
        sa_column=Column(
            ForeignKey("discipline.id", ondelete="CASCADE")
        )
    ) # disciplineOid
    auditorium_id: int = Field(
        sa_column=Column(
            ForeignKey("auditorium.id", ondelete="CASCADE")
        )
    ) # auditoriumOid
    lecturer_id: int = Field(
        sa_column=Column(
            ForeignKey("lecturer.id", ondelete="CASCADE")
        )
    )
    date: datetime.date = Field(default=datetime.datetime.now(timezone.utc))

    begin_lesson: datetime.date = Field(sa_column=Column(
        "begin_lesson",
        Time,
        nullable=False
    ))
    end_lesson: datetime.date = Field(sa_column=Column(
        "end_lesson",
        Time,
        nullable=False
    ))
    updated_at: datetime.datetime = Field(default=datetime.datetime.now(timezone.utc))
    sub_group: int = Field(default=0)

    kind_of_work: Optional[KindOfWork] = Relationship(back_populates="lessons")
    discipline: Optional[Discipline] = Relationship(back_populates="lessons")
    auditorium: Optional[Auditorium] = Relationship(back_populates="lessons")
    lecturer: Optional[Lecturer] = Relationship(back_populates="lessons")
    groups: List["Group"] = Relationship(
        link_model=LessonGroup
    )
