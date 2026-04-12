import asyncio
import calendar
import logging
from datetime import date, datetime, time, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import aiohttp
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LessonCreate(BaseModel):
    """
    About:
        Pydantic model for representing lesson creation data.

    Args:
        id (int): Unique identifier for the lesson (lessonOid).
        lecturer_id (int): Unique identifier for the lecturer.
        lecturer_guid (UUID): Universally unique identifier for the lecturer.
        lecturer_full_name (str): Full name of the lecturer.
        lecturer_short_name (str): Short name of the lecturer.
        lecturer_rank (str): Academic rank of the lecturer.
        kind_of_work_id (int): Identifier for the type of work/kind of lesson.
        type_of_work (str): Type of lesson work (e.g., lecture, seminar).
        complexity (int): Complexity level of the lesson.
        discipline_id (int): Unique identifier for the discipline/subject.
        discipline_name (str): Name of the discipline/subject.
        auditorium_id (int): Unique identifier for the auditorium.
        auditorium_guid (UUID): Universally unique identifier for the auditorium.
        auditorium_name (str): Name of the auditorium.
        auditorium_building (str): Building where the auditorium is located.
        date (date): The date of the lesson.
        begin_lesson (time): Start time of the lesson.
        end_lesson (time): End time of the lesson.
        group_id (int): Identifier for the student group.
        sub_group (int, optional): Subgroup number, defaults to 0.

    Returns:
        LessonCreate: An instance containing all lesson-related fields.
    """

    id: int  # lessonOid
    lecturer_id: int
    lecturer_guid: UUID
    lecturer_full_name: str
    lecturer_short_name: str
    lecturer_rank: str

    kind_of_work_id: int
    type_of_work: str
    complexity: int

    discipline_id: int  # lesson Oid
    discipline_name: str

    auditorium_id: int
    auditorium_guid: UUID
    auditorium_name: str
    auditorium_building: str

    date: date
    begin_lesson: time
    end_lesson: time

    group_id: int
    sub_group: int = 0


class RuzAPI:
    """
    RuzAPI provides methods to interact with the RUZ (Расписание учебных занятий) system,
    including methods for fetching schedule, group, and lesson data from the remote API,
    and utility functions for request handling and date calculations.

    Args:
        None (class does not accept constructor arguments by default)

    Returns:
        RuzAPI: An instance containing methods for communicating with the RUZ system.
    """

    LESSONS_URL = "https://ruz.mstuca.ru/api/schedule/group/{}?start={}&finish={}&lng=1"
    GROUP_SEARCH_URL = "https://ruz.mstuca.ru/api/search"

    async def _sleep(self, response: aiohttp.ClientResponse, backoff: int):
        """
        Sleeps for the given backoff time or the Retry-After value in the response
        headers if present. The backoff time is doubled after each sleep.

        Args:
            response (aiohttp.ClientResponse): The aiohttp response.
            backoff (int): The initial backoff time in seconds.

        Returns:
            int: The new backoff time in seconds.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None and retry_after.isdigit():
            delay = int(retry_after)
            logger.warning(f"Received 429, Retry-After={delay}s; sleeping {delay}s")
            await asyncio.sleep(delay)
        else:
            logger.warning(f"Received 429 without Retry-After; sleeping {backoff}s")
            await asyncio.sleep(backoff)

        return backoff * 2

    async def _get_borders_for_schedule(self):
        """
        Computes the start and end dates of the previous, current and next month

        Returns:
            tuple: start and end dates as strings in the format "%Y.%m.%d"
        """
        first_this_month = datetime.today().replace(day=1)
        first_prev_month = (first_this_month - timedelta(days=2)).replace(day=1)

        last_day_this_month = calendar.monthrange(
            first_this_month.year, first_this_month.month
        )[1]
        last_this_month = first_this_month + timedelta(days=last_day_this_month - 1)

        first_next_month = (last_this_month + timedelta(days=2)).replace(day=1)
        last_day_next_month = calendar.monthrange(
            first_next_month.year, first_next_month.month
        )[1]
        last_next_month = first_next_month + timedelta(days=last_day_next_month - 1)

        start_str = first_prev_month.strftime("%Y.%m.%d")
        end_str = last_next_month.strftime("%Y.%m.%d")

        return start_str, end_str

    async def _parse_lessons(
        self, raw_data: dict, group_id: str, update_time: str
    ) -> list[dict]:
        """
        Parse raw lessons data from API response into a list of processed lessons
        with added group_id, subgroup and update_time fields.

        Args:
            raw_data (dict): Raw lessons data from API response.
            group_id (str): Group ID.
            update_time (str): Update time in ISO format.

        Returns:
            List[dict]: Processed lessons list.
        """
        processed = []
        for lesson in raw_data:
            subgroup = 0
            list_sub = lesson.get("listSubGroups", [])
            if list_sub:
                subgroup = int(list_sub[0].get("subgroup")[-1])

            full_name = lesson["listOfLecturers"][0]["lecturer_title"]
            lesson_date = datetime.strptime(lesson["date"], "%Y.%m.%d").date()
            begin_lesson = datetime.strptime(lesson["beginLesson"], "%H:%M").time()
            end_lesson = datetime.strptime(lesson["endLesson"], "%H:%M").time()

            lesson = LessonCreate(
                id=lesson["lessonOid"],
                lecturer_id=lesson["lecturerOid"],
                lecturer_guid=lesson["lecturerCustomUID"],
                lecturer_full_name=full_name,
                lecturer_short_name=lesson["lecturer"],
                lecturer_rank=lesson["lecturer_rank"],
                kind_of_work_id=lesson["kindOfWorkOid"],
                type_of_work=lesson["typeOfWork"],
                complexity=lesson["kindOfWorkComplexity"],
                discipline_id=lesson["disciplineOid"],
                discipline_name=lesson["discipline"],
                auditorium_id=lesson["auditoriumOid"],
                auditorium_guid=lesson["auditoriumGUID"],
                auditorium_name=lesson["auditorium"],
                auditorium_building=lesson["building"],
                date=lesson_date,
                begin_lesson=begin_lesson,
                end_lesson=end_lesson,
                group_id=group_id,
                sub_group=subgroup,
            )

            processed.append(lesson)

        return processed

    async def _fetch(self, client: aiohttp.ClientSession, url: str, ssl=True) -> Any:
        """
        Fetches JSON data from the given URL.

        Args:
            client (aiohttp.ClientSession): The aiohttp client session.
            url (str): The URL to fetch.

        Returns:
            Parsed JSON (object or array, depending on the endpoint).
        """
        max_retries = 5
        backoff = 1  # initial backoff in seconds

        for attempt in range(1, max_retries + 1):
            logger.debug(f"[Attempt {attempt}] Fetching URL: {url}")
            async with client.get(url=url, ssl=ssl) as response:
                if response.status == 429:
                    backoff = await self._sleep(response, backoff)
                    continue

                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                    response.raise_for_status()

                data = await response.json(encoding="Windows-1251")
                logger.debug(
                    f"Successfully received data ({len(str(data))} bytes) from {url}"
                )
                return data

        raise aiohttp.ClientError(f"Exceeded {max_retries} retries for URL: {url}")

    async def get(self, group: str, start_date: str, end_date: str) -> dict:
        """
        Parse schedule for group from start_date to end_date

        Args:
            group (str): Group name
            start_date (str): Start date in format %Y.%m.%d
            end_date (str): End date in format %Y.%m.%d

        Returns:
            dict: Schedule in JSON format
        """
        logger.info(
            f"Running parse for group={group}, start={start_date}, end={end_date}"
        )
        async with aiohttp.ClientSession() as session:
            json_data = await self._fetch(
                session,
                RuzAPI.LESSONS_URL.format(group, start_date, end_date),
                ssl=False,
            )

        logger.debug(f"parse returned {len(json_data)} entries for group={group}")
        return json_data

    async def getDay(self, group: str, date: datetime) -> dict:
        """
        Parse schedule for group for one day

        Args:
            group (str): Group name
            date (datetime): date

        Returns:
            dict: Schedule in JSON format
        """
        date_str = date.strftime("%Y.%m.%d")
        logger.info(f"parseDay called for group={group}, date={date_str}")
        result = await self.get(group, date_str, date_str)
        logger.debug(
            f"parseDay returned {len(result)} lessons for {group} on {date_str}"
        )
        return result

    async def getWeek(self, group: str, date: datetime) -> list[dict]:
        """
        Parse schedule for group for one week

        Args:
            group (str): Group name
            date (datetime): date

        Returns:
            List[dict]: Schedule in JSON format
        """
        logger.info(f"parseWeek called for group={group}, base_date={date.date()}")
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)

        start_str = start.strftime("%Y.%m.%d")
        end_str = end.strftime("%Y.%m.%d")

        logger.debug(f"Week range for {group}: {start_str} - {end_str}")
        result = await self.get(group, start_str, end_str)
        logger.debug(
            f"parseWeek returned {len(result)} lessons for {group} week starting {start_str}"
        )
        return result

    async def getSchedule(self, group_id: str) -> list[dict]:
        """
        Parse schedule for group for three month

        Args:
            group_id (str): Group id

        Returns:
            List[dict]: Schedule in JSON format
        """
        logger.info(f"parseSchedule called for group={group_id}")

        start_str, end_str = await self._get_borders_for_schedule()
        update_time = datetime.now().isoformat()

        logger.debug(
            f"Month bounds for {group_id}: start={start_str}, end={end_str}, update_time={update_time}"
        )
        raw_data = await self.get(group_id, start_str, end_str)
        processed = await self._parse_lessons(raw_data, group_id, update_time)

        if not processed:
            logger.warning(f"No lessons returned for group {group_id}")
            return []

        logger.info(
            f"parseSchedule completed with {len(processed)} lessons for {group_id}"
        )
        return processed

    async def getGroup(self, group_name: str) -> list[dict]:
        """
        Search group in MSTUCA

        Args:
            group_name (str): Group name

        Returns:
            List[dict]: List of groups
        """
        logger.info(f"search_group called for name={group_name!r}")
        query = urlencode({"term": group_name, "type": "group"})
        url = f"{RuzAPI.GROUP_SEARCH_URL}?{query}"
        async with aiohttp.ClientSession() as session:
            json_data = await self._fetch(session, url, ssl=False)
        logger.debug(
            f"search_group returned {len(json_data)} results for {group_name!r}"
        )
        return json_data
