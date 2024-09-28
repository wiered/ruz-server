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
        query = "SELECT COUNT(id) FROM users WHERE id = %s"
        params = (user_id, )

        self.cur.execute(query, params)

        return self.cur.fetchone()[0] == 1

    def isGroupInDB(
        self,
        group_id: int
        ) -> bool:
        query = "SELECT COUNT(id) FROM groups WHERE id = %s"
        params = (group_id, )

        self.cur.execute(query, params)

        return self.cur.fetchone()[0] == 1

    def isDateRangeInDB(
        self,        group_id: str,
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
        query = """
            SELECT users.id, users.group_id, groups.name, users.sub_group, users.is_premium FROM users
            INNER JOIN groups ON groups.id = users.group_id
            WHERE users.id = %s
        """
        params = (user_id, )

        self.cur.execute(query, params)

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

        query = """INSERT INTO users (id, group_id, sub_group, is_premium) VALUES (%s, %s, %s, %s)"""
        params = (user_id, group_id, sub_group, is_premium)

        self.cur.execute(query, params)
        self._commit()

    def updateUser(
        self,
        id: int,
        group_id: int,
        group_name: str,
        sub_group: int = 0,
        is_premium: bool = False
        ):
        # Add group first to prevent concurrent access issues
        self.addGroup(group_id, group_name)

        query = """
            UPDATE users
            SET
                group_id = %s,
                sub_group = %s,
                is_premium = %s
            WHERE id = %s;
        """

        params = (group_id, sub_group, is_premium, id)

        self.cur.execute(query, params)
        self._commit()

    def updateUserGroup(
            self,
            user_id: int,
            group_id: int,
            group_name: str,
            sub_group: int = 0
    ):
        query = """
            UPDATE users
            SET
                group_id = %s,
                sub_group = %s
            WHERE id = %s;
        """

        params = (group_id, sub_group, user_id)

        self.cur.execute(query, params)
        self._commit()

    def deleteUser(
        self,
        user_id: int
        ):
        query = """
            DELETE FROM users
            WHERE id = %s;
        """
        params = (user_id, )

        self.cur.execute(query, params)
        self._commit()

    # ========================

    # ========================
    # Group
    def getGroup(
        self,
        id: int
        ) -> models.Group:
        params = (id, )
        query = "SELECT * FROM groups WHERE id = %s"
        self.cur.execute(query, params)

        return models.Group(*self.cur.fetchone())

    def getGroups(self) -> List[int]:
        self.cur.execute(f"SELECT * FROM groups")

        return [ {
           "id": group[0],
           "name": group[1]
        } for group in self.cur.fetchall()]

    def addGroup(self, id: int, name: str):
        query = """
            INSERT INTO groups (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
        """

        params = (id, name)

        self.cur.execute(query, params)
        self._commit()

    def getUserCountByGroup(
        self,
        group_id: int
        ) -> int:
        query = """
            SELECT COUNT(id) FROM users
            WHERE group_id = %s
        """
        params = (group_id, )

        self.cur.execute(query, params)
        return self.cur.fetchone()[0]

    def deleteGroup(
        self,
        id: int
        ):
        query = """
            DELETE FROM groups
            WHERE id = %s
        """
        params = (id, )

        self.cur.execute(query, params)
        self._commit()

    # ========================
    # Schedule

    def getSchedule(
        self,
        group_id: int
        ) -> List[models.LessonDB]:
        query = """
            SELECT * FROM lessons
            WHERE group_id = %s
        """
        params = (group_id, )

        self.cur.execute(query, params)
        return [models.LessonDB(*lesson) for lesson in self.cur.fetchall()]

    def getScheduleInRange(
        self,
        group_id: int,
        start_date: str,
        end_date: str,
        sub_group: int = 0
    ) -> List[models.LessonDB]:
        query = """
            SELECT * FROM lessons
            WHERE
                group_id = %s AND date >= %s::date AND date <= %s::date
                AND (sub_group = %s OR sub_group = 0 OR %s = 0)
        """

        params = (group_id, start_date, end_date, sub_group, sub_group)

        self.cur.execute(query, params)
        return [models.LessonDB(*lesson) for lesson in self.cur.fetchall()]

    def getScheduleForDay(
        self,
        group_id: int,
        sub_group: int,
        date: datetime
    ) -> List[models.LessonDB]:

        if not self.isGroupInDB(group_id):
            return []

        return self.getScheduleInRange(group_id, date, date, sub_group)

    def getScheduleForWeek(
        self,
        group_id: int,
        sub_group: int,
        date: datetime
        ) -> list[models.LessonDB]:

        if not self.isGroupInDB(group_id):
            return []

        start_time, end_time = utils.getStartAndEndOfWeek(datetime.strptime(date, "%Y-%m-%d"))

        return self.getScheduleInRange(group_id, start_time, end_time, sub_group)

    def addLessonToSchedule(
        self,
        lesson: models.LessonDB
    ):
        query = """
            INSERT INTO lessons (
                discipline,
                kind_of_work,
                auditorium,
                date,
                beginLesson,
                endLesson,
                lecturer_title,
                lecturer_rank,
                sub_group,
                group_id
            )
            VALUES (%s, %s, %s, %s::date, %s, %s, %s, %s, %s, %s)
        """

        params = (
            lesson.discipline,
            lesson.kind_of_work,
            lesson.auditorium,
            lesson.date,
            lesson.beginLesson,
            lesson.endLesson,
            lesson.lecturer_title,
            lesson.lecturer_rank,
            lesson.sub_group,
            lesson.group_id
        )

        self.cur.execute(query, params)
        self._commit()

    def addScheduleToDB(
        self,
        group_id: str,
        schedule: List[dict]
        ):
        self.deleteScheduleFromDB(group_id)
        for lesson in schedule:
            self.addLessonToSchedule(lesson)

    def deleteScheduleFromDB(self, group_id: int):
        query = """
            DELETE FROM lessons
            WHERE group_id = %s;
        """

        self.cur.execute(query, (group_id,))
        self._commit()

    # ========================
