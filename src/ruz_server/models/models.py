import datetime
from datetime import timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlmodel import Column, Field, Relationship, SQLModel


class LessonGroup(SQLModel, table=True):
    """
    LessonGroup model represents the association table between lessons and groups.

    Args:
        lesson_id (int): ID of the associated lesson.
        group_id (int): ID of the associated group.

    Returns:
        LessonGroup: The association between a lesson and a group.
    """
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

    lesson: Optional["Lesson"] = Relationship(
        back_populates="lesson_groups",
        sa_relationship_kwargs={"overlaps": "groups,lessons"},
    )
    group: Optional["Group"] = Relationship(
        back_populates="lesson_groups",
        sa_relationship_kwargs={"overlaps": "groups,lessons"},
    )


class Group(SQLModel, table=True):
    """
    Group model represents a student group within the university.

    Args:
        id (int): The unique identifier of the group (groupOid).
        guid (UUID): The unique UUID of the group.
        name (str): The name of the group.
        faculty_name (str): The name of the faculty this group belongs to.

    Returns:
        Group: An instance representing a university group.
    """
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
    lesson_groups: List["LessonGroup"] = Relationship(
        back_populates="group",
        sa_relationship_kwargs={"overlaps": "lessons,groups"},
    )
    lessons: List["Lesson"] = Relationship(
        back_populates="groups",
        link_model=LessonGroup,
        sa_relationship_kwargs={"overlaps": "group,lesson,lesson_groups"},
    )


class User(SQLModel, table=True):
    """
    User model represents a user within the system, typically corresponding to a Telegram user.

    Args:
        id (int): The unique identifier of the user (Telegram ID).
        group_oid (int): The unique identifier (OID) for the user's group. May be null if not assigned.
        subgroup (Optional[int]): The subgroup number the user belongs to.
        username (str): The username of the user.
        created_at (datetime.datetime): The timestamp when the user was created in the system.
        last_used_at (datetime.datetime): The timestamp when the user last interacted with the system.

    Returns:
        User: An instance representing a user in the system.
    """
    __tablename__ = "users"
    id: int = Field(
        sa_column=Column(
            "id",
            BigInteger,
            primary_key=True
        )
    ) # telegram id
    group_oid: Optional[int] = Field(
        sa_column=Column(
            ForeignKey("groups.id", ondelete="SET NULL"),
            nullable=True
        )
    )
    subgroup: Optional[int] = Field(default=None, nullable=True)
    username: str = Field(sa_column=Column(
        "username",
        String,
        nullable=False
    ))
    created_at: datetime.datetime = Field(default=datetime.datetime.now(timezone.utc))
    last_used_at: datetime.datetime = Field(default=datetime.datetime.now(timezone.utc))

    group: Optional[Group] = Relationship(back_populates="users")


class Lecturer(SQLModel, table=True):
    """
    Lecturer model represents a lecturer entity in the system.

    Args:
        id (int): The unique identifier for the lecturer (lecturerOid).
        guid (UUID): The globally unique identifier for the lecturer (lecturerGUID).
        full_name (str): The full name of the lecturer.
        short_name (str): The short name or abbreviated name of the lecturer.
        rank (str): The academic or professional rank of the lecturer.

    Returns:
        Lecturer: An instance representing a lecturer in the system.
    """
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
    """
    KindOfWork model represents a type of work (for example, lecture, seminar, lab work) associated with lessons.

    Args:
        id (int): The unique identifier for the kind of work (kindOfWorkOid).
        type_of_work (str): A string describing the type of work.
        complexity (int): An integer representing the complexity level of the work.

    Returns:
        KindOfWork: An instance representing a type of work associated with lessons.
    """
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
    """
    Discipline model represents an academic discipline or subject, such as Mathematics, Physics, etc.

    Args:
        id (int): The unique identifier for the discipline (disciplineOid).
        name (str): The name of the discipline.
        examtype (str): The type of exam associated with the discipline.
        has_labs (bool): Indicates whether the discipline includes laboratory works.

    Returns:
        Discipline: An instance representing an academic discipline.
    """
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
    """
    Auditorium model represents a physical location where lessons or events are held, such as classrooms, lecture halls, or laboratories.

    Args:
        id (int): Unique identifier for the auditorium (auditoriumOid).
        guid (UUID): Globally unique identifier for the auditorium (auditoriumGUID).
        name (str): Name of the auditorium.
        building (str): Building to which the auditorium belongs.

    Returns:
        Auditorium: An instance representing a physical place where lessons occur.
    """
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
    """
    Lesson model represents a scheduled class, lecture, or educational event.

    Args:
        id (int): Unique identifier for the lesson (lessonOid).
        kind_of_work_id (int): Foreign key referencing the kind of work for the lesson.
        discipline_id (int): Foreign key referencing the discipline associated with the lesson.
        auditorium_id (int): Foreign key referencing the auditorium where the lesson is held.
        lecturer_id (int): Foreign key referencing the lecturer giving the lesson.
        date (datetime.date): Date when the lesson takes place.
        begin_lesson (datetime.time): Time when the lesson begins.
        end_lesson (datetime.time): Time when the lesson ends.
        updated_at (datetime.datetime): Timestamp when the lesson was last updated.
        sub_group (int): Subgroup identifier for the lesson (default is 0).
        kind_of_work (Optional[KindOfWork]): Relationship to the kind of work entity.
        discipline (Optional[Discipline]): Relationship to the discipline entity.
        auditorium (Optional[Auditorium]): Relationship to the auditorium entity.
        lecturer (Optional[Lecturer]): Relationship to the lecturer entity.
        lesson_groups (List["LessonGroup"]): Relationships to lesson-group associations.
        groups (List["Group"]): Relationships to group entities via lesson groups.

    Returns:
        Lesson: An instance representing a scheduled lesson or class event.
    """
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

    # SQL column type is TIME, so the Python-side type must be datetime.time.
    begin_lesson: datetime.time = Field(sa_column=Column(
        "begin_lesson",
        Time,
        nullable=False
    ))
    end_lesson: datetime.time = Field(sa_column=Column(
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
    lesson_groups: List["LessonGroup"] = Relationship(
        back_populates="lesson",
        sa_relationship_kwargs={"overlaps": "lessons,groups"},
    )
    groups: List["Group"] = Relationship(
        back_populates="lessons",
        link_model=LessonGroup,
        sa_relationship_kwargs={"overlaps": "group,lesson,lesson_groups"},
    )
