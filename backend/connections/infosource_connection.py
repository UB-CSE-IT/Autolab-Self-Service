import logging
from typing import List, Dict, Any

import cachetools.func
import oracledb

from backend.connections.course import Course
from backend.utils import twelve_hour_time_to_24_hour_time, class_meeting_pattern_source_key_to_days_code

logger = logging.getLogger("portal")


class InfoSourceConnection:
    def __init__(self, username: str, password: str, dsn: str):
        logger.debug(f"Connecting to InfoSource database {dsn} as {username}")
        self.username = username
        self.password = password
        self.dsn = dsn
        self.con = None
        self.cursor = None
        oracledb.init_oracle_client()
        logger.debug("Successfully connected to InfoSource database")

    def __enter__(self):
        self.con = oracledb.connect(user=self.username, password=self.password, dsn=self.dsn)
        self.cursor = self.con.cursor()
        return self.cursor

    def __exit__(self, *args):
        self.cursor.close()
        self.con.close()
        self.cursor = None
        self.con = None

    def query_all_courses(self) -> List[Course]:
        logger.debug("Querying all courses from InfoSource database")
        stmt = """ \
            SELECT SUBJECTSOURCEKEY,
                SUBSTR(CATALOGNUMBERSOURCEKEY, 1, 3) as COURSENUMBER,
                COURSE,
                COURSETYPE,
                TERM,
                COMBINEDSECTIONID,
                TERMSOURCEKEY,
                COURSEID,
                CLASSNUMBER,
                PRINCIPAL                            as INSTRUCTOR
            FROM PS_RPT.CLASSSCHEDULE_V
                JOIN DCE.PERSON_NUMBER ON CLASSSCHEDULE_V.FACULTYSOURCEKEY = PERSON_NUMBER.PERSON_NUMBER
            AND COURSETYPESOURCEKEY NOT IN ('LAB', 'TUT', 'REC')
            AND ENDDATE > CURRENT_DATE
            GROUP BY SUBJECTSOURCEKEY,
            SUBSTR(CATALOGNUMBERSOURCEKEY, 1, 3),
            COURSE,
            COURSETYPE,
            TERM,
            COMBINEDSECTIONID,
            TERMSOURCEKEY,
            COURSEID,
            CLASSNUMBER,
            PRINCIPAL,
            ENDDATE
            ORDER BY ENDDATE, COURSENUMBER
              """

        with self as info:
            info.execute(stmt)
            # Put the results into a Course based on https://stackoverflow.com/a/57108771
            info.rowfactory = lambda *args: Course(*args)
            rows = info.fetchall()
            return rows

    @cachetools.func.ttl_cache(maxsize=10, ttl=600)
    def get_course_sections_by_autolab_course_name(self, autolab_course_name: str):
        # autolab_course_name will be like "cse116-f21" or "cse442-u23b"

        course_name: str  # "cse116" or "cse442"
        semester_code: str  # "f21" or "u23b"
        course_name, semester_code = autolab_course_name.split('-', 1)
        year: str = f"20{semester_code[1:3]}"  # "2021" or "2023", will break after 2099
        season_map: Dict[str, str] = {
            "f": "Fall",
            "w": "Winter",
            "s": "Spring",
            "u": "Summer"
        }
        season = season_map[semester_code[0]]  # "Fall", "Winter", "Spring", or "Summer"
        subject: str = course_name[:3].upper()  # "CSE"
        course_number: str = course_name[3:]  # "116" or "442"

        stmt = """ \
            SELECT CLASSMEETINGPATTERNSOURCEKEY,
            CLASSSECTIONSOURCEKEY,
            CLASSSTARTTIME,
            CLASSENDTIME,
            COURSETYPESOURCEKEY
            FROM PS_RPT.CLASSSCHEDULE_V
            WHERE SUBJECTSOURCEKEY = :subject
              AND CATALOGNUMBERSOURCEKEY LIKE :course_number
              AND TERM = :term
        """

        with self as info:
            info.execute(stmt, subject=subject, course_number=f"{course_number}%", term=f"{season} {year}")
            rows = info.fetchall()
            # This looks like: [
            # ('M', 'R33', '5:00PM', '5:50PM', 'REC'),
            # ('MWF', 'A', '8:00AM', '8:50AM', 'LEC'),
            # ('M', 'A1', '12:00PM', '1:50PM', 'LAB'),...]

        sections: List[Dict[str, Any]] = []
        for row in rows:
            try:
                sections.append({
                    "name": row[1],
                    "days_code": class_meeting_pattern_source_key_to_days_code(row[0]),
                    "start_time": twelve_hour_time_to_24_hour_time(row[2]),
                    "end_time": twelve_hour_time_to_24_hour_time(row[3]),
                    "is_lecture": row[4] == "LEC"
                })
            except Exception as e:
                logger.error(f"Error parsing section {row[1]}: {e}")
                logger.error(f"Row: {row}")
                logger.error("Skipping section")
                pass

        return sections

    def get_person_info_by_username(self, username: str):
        logger.debug(f"Querying person info for {username} from InfoSource database")
        stmt = """ \
            SELECT FIRST_NAME, LAST_NAME, PERSON_NUMBER, PRINCIPAL AS USERNAME
            FROM DCE.PERSON_NUMBER
                 JOIN PS_RPT.UB_DISPLAY_NAME_V ON DCE.PERSON_NUMBER.PERSON_NUMBER = PS_RPT.UB_DISPLAY_NAME_V.EMPLID
            WHERE PRINCIPAL = :username
        """
        with self as info:
            info.execute(stmt, username=username)
            # Based on https://stackoverflow.com/a/57108771
            info.rowfactory = lambda *args: dict(zip([d[0] for d in info.description], args))
            result = info.fetchone()
            return result
