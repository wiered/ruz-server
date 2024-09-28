from datetime import datetime
from typing import List

import psycopg2

import models
import utils

CREATE_GROUPS_TABLE = """CREATE TABLE IF NOT EXISTS groups (
    id BIGINT PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);"""

CREATE_USERS_TABLE ="""CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    group_id BIGINT NOT NULL,
    sub_group BIGINT NOT NULL,
    is_premium BOOL NOT NULL,
    CONSTRAINT user_group_id_fk FOREIGN KEY (group_id) REFERENCES groups (id)
);"""

CREATE_LESSONS_TABLE = """CREATE TABLE IF NOT EXISTS lessons (
    discipline VARCHAR(40) NOT NULL,
    kind_of_work VARCHAR(40) NOT NULL,
    auditorium VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    beginLesson TIME NOT NULL,
    endLesson TIME NOT NULL,
    lecturer_title VARCHAR(40) NOT NULL,
    lecturer_rank VARCHAR(40) NOT NULL,
    sub_group BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    id BIGSERIAL PRIMARY KEY,
    CONSTRAINT lesson_group_id_fk FOREIGN KEY (group_id) REFERENCES groups (id)
);"""


class DB:
    def __init__(self, dbname, user, host, password, port = 5432):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password
        self.port = port

        self.conn = self._connect()
        self.cur = self._get_cursor()

        self._createTables()

    def _get_cursor(self):
        return self.conn.cursor()

    def _connect(self):
        return psycopg2.connect(dbname=self.dbname, user=self.user, host=self.host, password=self.password, port=self.port)

    def _commit(self):
        self.conn.commit()

    def _close(self):
        self._commit()
        self.cur.close()
        self.conn.close()

    def _createTable(self, SQL):
        try:
            self.cur.execute(SQL)
        except:
            self.conn.rollback()

    def _createTables(self):
        self._createTable(CREATE_GROUPS_TABLE)
        self._createTable(CREATE_USERS_TABLE)
        self._createTable(CREATE_LESSONS_TABLE)

        self._commit()

    # ========================
    # Exists
    def isUserKnown(
        self,
        user_id: int
        ) -> bool:
        self.cur.execute(f"SELECT COUNT(id) FROM users WHERE id = {user_id}")

        return self.cur.fetchone()[0] == 1

    def isGroupInDB(
        self,
        group_id: int
        ) -> bool:
        self.cur.execute(f"SELECT COUNT(id) FROM groups WHERE id = {group_id}")

        return self.cur.fetchone()[0] == 1

    def isDateRangeInDB(
        self,
        group_id: str,
        start: str,
        end: str
        ) -> bool:
        # If the group is not cached, the day is not cached
        # If group is not chached, the day is not cached
        if not self.isGroupInDB(group_id):
            return False

        start = datetime.strptime(start, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")

        # Get the bounds of the previous and next month
        reference_date = datetime.now()
        start_of_previous_month, end_of_next_month = utils.getPreviousAndNextMonthBounds(reference_date)

        # Check if the start of range is before the start of the previous month
        if (start - start_of_previous_month).total_seconds() < 0:
            # If it is, the range is not cached
            return False

        # Check if the end of range is after the end of the next month
        if (end_of_next_month - end).total_seconds() < 0:
            # If it is, the range is not cached
            return False

        # If the date is between the start of the previous month and the end of the next month
        # and the group is cached, then the day is cached
        return True

    def isDayInDB(
        self,
        group_id: int,
        date: str
        ) -> bool:
        return self.isDateRangeInDB(group_id, date, date)

    def isWeekInDB(
        self,
        group_id: int,
        date: str
        ):
        start, end = utils.getStartAndEndOfWeek(datetime.strptime(date, "%Y-%m-%d"))
        return self.isDateRangeInDB(group_id, start, end)

    # ========================

    # ========================
    # User
    def getUser(
        self,
        user_id: int
        ) -> models.User:
        self.cur.execute(f"""SELECT users.id, users.group_id, groups.name, users.sub_group, users.is_premium FROM users
INNER JOIN groups ON groups.id = users.group_id
WHERE users.id = {user_id}""")

        return models.User(*self.cur.fetchone())

    def addUser(
        self,
        user_id: int,
        group_id: int,
        group_name: str,
        sub_group: int = 0,
        is_premium: bool = False
        ):
        if self.isUserKnown(user_id):
            raise Exception("User already exists")

        self.addGroup(group_id, group_name)

        self.cur.execute(f"""INSERT INTO users (id, group_id, sub_group, is_premium) VALUES
({user_id}, {group_id}, {sub_group}, {is_premium});
""")

        self._commit()

    def updateUser(
        self,
        user_id: int,
        group_id: int,
        group_name: str,
        sub_group: int = 0,
        is_premium: bool = False
        ):
        self.addGroup(group_id, group_name)

        self.cur.execute(f"""UPDATE users SET
group_id = {group_id},
sub_group = {sub_group},
is_premium = {is_premium}
WHERE id = {user_id};
""")
        self._commit()

    def updateUserGroup(
        self ,
        user_id: int,
        group_id: int,
        group_name: str,
        sub_group: int = 0
        ):
        self.addGroup(group_id, group_name)

        self.cur.execute(f"""UPDATE users SET
group_id = {group_id},
sub_group = {sub_group}
WHERE id = {user_id};
""")
        self._commit()

    def deleteUser(
        self,
        user_id: int
        ):
        self.cur.execute(f"""DELETE FROM users
WHERE id = {user_id};
""")

    # ========================

    # ========================
    # Group
    def getGroup(
        self,
        id: int
        ) -> models.Group:
        self.cur.execute(f"SELECT * FROM groups WHERE id = {id}")

        return models.Group(*self.cur.fetchone())

    def getGroups(self) -> List[int]:
        self.cur.execute(f"SELECT id FROM groups")
        return [group[0] for group in self.cur.fetchall()]

    def addGroup(self, id: int, name: str):
        self.cur.execute(f"""
    INSERT INTO groups (id, name)
    VALUES ({id}, '{name}')
    ON CONFLICT (id) DO NOTHING;
""")
        self._commit()

    def getUserCountByGroup(
        self,
        group_id: int
        ) -> int:
        self.cur.execute(f"SELECT COUNT(id) FROM users WHERE group_id = {group_id}")

        return self.cur.fetchone()[0]

    # ========================
    # Schedule

    def getSchedule(
        self,
        group_id: int
        ) -> List[models.Lesson]:
        self.cur.execute(f"""SELECT * FROM lessons
WHERE group_id = {group_id}""")

        return [models.Lesson(*lesson) for lesson in self.cur.fetchall()]

    def getScheduleInRange(
        self,
        group_id: int,
        start_date: str,
        end_date: str,
        sub_group: int = 0
        ) -> List[models.Lesson]:
        self.cur.execute(f"""SELECT * FROM lessons
WHERE group_id = {group_id}
AND date >= '{start_date}'::date
AND date <= '{end_date}'::date
AND (sub_group = {sub_group} OR sub_group = 0 OR {sub_group} = 0)""")

        return [models.Lesson(*lesson) for lesson in self.cur.fetchall()]

    def getScheduleForDay(
        self,
        user_id: int,
        date: datetime
        ) -> List[models.Lesson]:
        """
        Get lessons for a user on a specific day

        Args:
            user_id (int): Telegram user id
            date (datetime): Date

        Returns:
            List[models.Lesson]: List of lessons
        """
        user = self.getUser(user_id)
        group_id = user.group_id
        sub_group = user.sub_group

        if (
            not self.isUserKnown(user_id) or
            not self.isGroupInDB(group_id) or
            not self.isWeekInDB(group_id, date)
            ):
            return []

        return self.getLessonsInDateRange(group_id, date, date, sub_group)

    def getScheduleForWeek(
        self,
        user_id: int,
        date: datetime
        ) -> list[models.Lesson]:
        user = self.getUser(user_id)
        group_id = user.group_id
        sub_group = user.sub_group

        # if (
        #     not self.isUserKnown(user_id) or
        #     not self.isGroupInDB(group_id) or
        #     not self.isWeekInDB(group_id, date)
        #     ):
        #     return []

        start_time, end_time = utils.getStartAndEndOfWeek(datetime.strptime(date, "%Y-%m-%d"))

        return self.getLessonsInDateRange(group_id, start_time, end_time, sub_group)

    def addLessonToSchedule(
        self,
        lesson: models.Lesson
    ):
        self.cur.execute(f"""INSERT INTO lessons
(discipline, kind_of_work, auditorium, date, beginLesson, endLesson, lecturer_title, lecturer_rank, sub_group, group_id)
VALUES (
'{lesson.discipline}',
'{lesson.kind_of_work}',
'{lesson.auditorium}',
'{lesson.date}',
'{lesson.beginLesson}',
'{lesson.endLesson}',
'{lesson.lecturer_title}',
'{lesson.lecturer_rank}',
{lesson.sub_group},
{lesson.group_id}
)
""")

        self._commit()

    def addScheduleToDB(
        self,
        group_id: str,
        lessons_for_this_month: List[dict]
        ):
        self.deleteScheduleFromDB(group_id)
        for lesson_json in lessons_for_this_month:
            lesson = models.Lesson(
                lesson_json.get("discipline"),
                lesson_json.get("kind_of_work"),
                lesson_json.get("auditorium"),
                lesson_json.get("date"),
                lesson_json.get("beginLesson"),
                lesson_json.get("endLesson"),
                lesson_json.get("lecturer_title"),
                lesson_json.get("lecturer_rank"),
                group_id
            )

            self.addLesson(lesson)

    def deleteScheduleFromDB(self, group_id: int):
        """
        Deletes the schedule for the given group from the database.

        Args:
            group_id (str): The ID of the group whose schedule should be deleted
        """
        self.cur.execute(f"""DELETE FROM lessons
WHERE group_id = {group_id};
""")
        self._commit()

    # ========================
