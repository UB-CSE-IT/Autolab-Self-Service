from typing import List
import oracledb

from backend.connections.Course import Course


class InfoSourceConnection:
    def __init__(self, username: str, password: str, dsn: str):
        self.username = username
        self.password = password
        self.dsn = dsn
        self.con = None
        self.cursor = None
        oracledb.init_oracle_client()

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
        stmt = """ \
            SELECT SUBJECTSOURCEKEY,
                SUBSTR(CATALOGNUMBERSOURCEKEY, 1, 3) as COURSENUMBER,
                COURSE,
                COURSETYPE,
                TERM,
                COMBINEDSECTIONID,
                TERMSOURCEKEY,
                CATALOGNUMBERSOURCEKEY,
                COURSESOURCEKEY,
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
            CATALOGNUMBERSOURCEKEY,
            COURSESOURCEKEY,
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

    def get_person_info_by_username(self, username: str):
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
