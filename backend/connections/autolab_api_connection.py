import logging
import time
from typing import List, Dict

import cachetools.func
import requests

logger = logging.getLogger("portal")


def store_refresh_token(refresh_token: str):
    with open("mount/refresh_token.txt", "w") as f:
        f.write(refresh_token)


def get_refresh_token_from_file() -> str:
    try:
        with open("mount/refresh_token.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_start_and_end_dates_for_semester(semester: str) -> tuple:
    # semester is a string like "f23"
    # Return a tuple of strings like ("2024-08-20", "2024-12-20")

    def get_current_year() -> int:
        return time.localtime().tm_year

    semester_to_start_end_dates = {
        "s": ("01-20", "05-20"),  # Spring is January 20th to May 20th
        "u": ("05-20", "08-20"),  # Summer is May 20th to August 20th
        "f": ("08-20", "12-20"),  # Fall is August 20th to December 20th
        "w": ("01-01", "02-01"),  # Winter is January 1st to February 1st
    }

    current_full_year = str(get_current_year())
    # This might not behave as expected in 2099, but we probably won't still be using this by then
    # I could have just hardcoded a "20" prefix, but this will work in the year 2100 :)
    start_date, end_date = semester_to_start_end_dates.get(semester[0])
    target_full_year = current_full_year[:2] + semester[1:]  # e.g. 20 + 23 = 2023
    return f"{target_full_year}-{start_date}", f"{target_full_year}-{end_date}"


class AutolabApiConnection:
    def __init__(self, path: str, client_id: str, client_secret: str, client_callback: str):
        self.__path = path
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__client_callback = client_callback
        self.__access_token = None

        if get_refresh_token_from_file() == "":
            logger.warning("No refresh token found, starting initial setup")
            self.__initial_setup()
        self.__get_new_access_token()

    @property
    def __refresh_token(self):
        return get_refresh_token_from_file()

    def __device_flow_init(self) -> dict:
        # Initiates the Ouath device flow
        # Returns a dict like:
        # {'device_code': 'abcd...',
        # 'user_code': 'abcd12',
        # 'verification_uri': 'http://localhost:81/activate'}
        logger.debug("Initiating OAuth device flow")
        url = f"{self.__path}/oauth/device_flow_init"
        params = {
            "client_id": self.__client_id,
        }
        r = requests.request("GET", url, params=params)
        return r.json()

    def __device_flow_authorize(self, device_code: str) -> dict:
        # Waits for the user to authorize the device flow
        # Uses the device_code from __device_flow_init
        # Returns a dict like:
        # {'code': 'fwM3PgwYfFd5S87b8HcSJrploQFHpoAj1ef3ME_FfmI'}
        logger.debug("Waiting for user to authorize device flow")
        url = f"{self.__path}/oauth/device_flow_authorize"
        params = {
            "client_id": self.__client_id,
            "device_code": device_code
        }
        while True:
            time.sleep(1)
            r = requests.request("GET", url, params=params)
            if "code" in r.json():
                break
        return r.json()

    def __get_initial_refresh_token(self, auth_code: str) -> dict:
        # Returns a dict like:
        # {'access_token': 'abcd...',
        #  'token_type': 'Bearer',
        #  'expires_in': 7199,
        #  'refresh_token':'efgh...',
        #  'scope': 'user_info user_courses user_scores user_submit instructor_all admin_all',
        #  'created_at': 1686757109}
        logger.debug("Getting initial refresh token")
        params = {
            "code": auth_code,
            "grant_type": "authorization_code",
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "redirect_uri": self.__client_callback
        }
        url = f"{self.__path}/oauth/token"
        r = requests.request("POST", url, params=params)
        return r.json()

    def __get_new_access_token(self):
        # Uses the refresh token stored on disk to get a new access token
        # Updates self.__access_token token in memory
        # Returns a dict like:
        # {'access_token': 'abcd...
        #  'token_type': 'Bearer',
        #  'expires_in': 7199,
        #  'refresh_token': 'efgh...',
        #  'scope': 'user_info user_courses user_scores user_submit instructor_all admin_all',
        #  'created_at': 1686760138}
        # Also updates the refresh token on disk with the new one received
        #  - important because the old one is invalidated
        logger.debug("Getting new access token")
        url = f"{self.__path}/oauth/token"
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.__refresh_token,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret
        }
        r = requests.request("POST", url, params=params)
        self.__access_token = r.json()["access_token"]
        store_refresh_token(r.json()["refresh_token"])
        return r.json()

    def __initial_setup(self):
        device_flow_init_resp = self.__device_flow_init()
        logger.info("Starting initial OAuth setup. This sensitive information will not be logged here. See stdout.")
        print(f"{device_flow_init_resp=}")
        device_flow_authorize_response = self.__device_flow_authorize(device_flow_init_resp["device_code"])
        print(f"{device_flow_authorize_response=}")
        auth_code = device_flow_authorize_response["code"]
        initial_refresh_token_resp = self.__get_initial_refresh_token(auth_code)
        print(f"{initial_refresh_token_resp=}")
        store_refresh_token(initial_refresh_token_resp["refresh_token"])
        logger.info("Initial OAuth setup complete")

    def make_api_request(self, method: str, path: str, params: dict, json=None, retry: bool = False) -> dict:
        # Makes a request to the Autolab API
        # method: GET, POST, PUT, DELETE, etc.
        # path: relative path to endpoint including leading slash (e.g. "/api/v1/courses")
        # params: dict of params to pass to the endpoint, excluding the access token
        # json: optional body to send as JSON
        # retry: True if this is a retry after a failed request due to an expired access token
        # Returns the response as a dict and handles refreshing the access token if needed
        # Raises an exception if the request fails even after refreshing the access token
        url = f"{self.__path}{path}"
        logger.debug(f"Making API request to {method} {url} with params: {params} ({retry=})")
        params["access_token"] = self.__access_token
        r = requests.request(method, url, json=json, params=params)
        if r.status_code != 200:
            logger.debug(f"API request failed with status code {r.status_code}")
            if r.status_code == 429:
                raise Exception("Autolab API rate limit exceeded. Try again in a few seconds.")
            if not retry:
                logger.debug("Trying again after getting a new access token")
                self.__get_new_access_token()
                del params["access_token"]
                return self.make_api_request(method, path, params, json=json, retry=True)
            logger.error(f"API request failed even after getting a new access token with status code {r.status_code}")
            message = "Response: " + r.text
            logger.error(message)
            raise Exception(message)
        else:
            logger.debug(f"API request succeeded. Returned {r.json()}")
            return r.json()

    def create_course(self, course_name: str, display_name: str, semester: str, instructor_email: str,
                      start_date: str, end_date: str) -> dict:
        params = {
            "name": f"{course_name}",  # Should include semester already, like "cse116-u23"
            "display_name": display_name,
            "semester": semester,
            "instructor_email": instructor_email,
            "start_date": start_date,
            "end_date": end_date
        }
        logger.info(f"Creating course {course_name} with params: {params}")
        return self.make_api_request("POST", "/api/v1/courses", params)

    def create_course_automatic_dates(self, course_name: str, display_name: str, semester: str,
                                      instructor_email: str) -> dict:
        logger.debug(f"Creating course {course_name} with automatic dates")
        start, end = get_start_and_end_dates_for_semester(semester)
        logger.debug(f"Calculated start date {start} and end date {end} for semester {semester}")
        return self.create_course(course_name, display_name, semester, instructor_email, start, end)

    def check_admin(self, email_address: str) -> bool:
        logger.info(f"Checking if {email_address} is an admin")
        params = {
            "email": email_address
        }
        return self.make_api_request("GET", "/api/ubcseit/admin_check", params).get("is_administrator", False)

    @cachetools.func.ttl_cache(maxsize=100, ttl=60)
    def user_courses(self, user_email: str) -> dict:
        # Returns a dict like:
        # {
        #   "email": "user@buffalo.edu",
        #   "courses": [
        #     {
        #       "name": "course1",  # The technical name of the course
        #       "display_name": "Course 1",  # The display name of the course
        #       "semester": "f23", # The semester code of the course
        #       "role": "student",  # or "instructor" or "course_assistant"
        #     }, ...
        #   ],
        # }
        # Courses are sorted by end_date, so the most recent course is last.
        logger.info(f"Getting Autolab courses for user {user_email}")
        params = {
            "email": user_email
        }
        return self.make_api_request("GET", "/api/ubcseit/user_courses", params)

    @cachetools.func.ttl_cache(maxsize=100, ttl=60)
    def course_users(self, course_name: str) -> dict:
        # Returns a dict like:
        # {
        #   "course_name": "course1",  # The technical name of the course
        #   "display_name": "Course 1",  # The display name of the course
        #   "users": [
        #     {
        #       "email": "example@buffalo.edu",
        #       "display_name": "First Last",
        #       "role": "student", # or "instructor" or "course_assistant"
        #     }, ...
        #   ],
        # }
        # Users are sorted alphabetically by email address.
        logger.info(f"Getting Autolab users for course {course_name}")
        params = {
            "course_name": course_name
        }
        return self.make_api_request("GET", "/api/ubcseit/course_users", params)

    @cachetools.func.ttl_cache(maxsize=100, ttl=60)
    def course_assessments(self, course_name: str) -> dict:
        # Returns a dict like:
        # {
        #   "course_name": "course1",  # The technical name of the course
        #   "display_name": "Course 1",  # The display name of the course
        #   "assessments": [
        #     {
        #       "name": "assessment1",  # The technical name of the assessment
        #       "display_name": "Assessment 1",  # The display name of the assessment
        #       "url": "https://autolab.cse.buffalo.edu/courses/cse-it-test-course/assessments/pdftest",
        #     }, ...
        #   ],
        # }
        # Assessments are sorted by due date, with the earliest due date first.
        logger.info(f"Getting Autolab assessments for course {course_name}")
        params = {
            "course_name": course_name
        }
        return self.make_api_request("GET", "/api/ubcseit/course_assessments", params)

    @cachetools.func.ttl_cache(maxsize=100, ttl=10)
    def get_assessment_submissions(self, course_name: str, assessment_name: str) -> dict:
        # Returns a dict like:
        # {
        #   "course_name": "course1",  # The technical name of the course
        #   "assessment_name": "assessment1",  # The technical name of the assessment
        #   "assessment_display_name": "Assessment 1",  # The display name of the assessment
        #   "submissions": [
        #     {
        #       "email": "somebody@buffalo.edu",
        #       "display_name": "First Last"
        #       "version": 22
        #       "url": "https://autolab.cse.buffalo.edu/courses/cse-it-test-course/assessments/pdftest/submissions/22/view",
        #     }, ...
        #   ],
        # }
        # Submissions are sorted alphabetically by email address.
        logger.info(f"Getting Autolab submissions for course {course_name} assessment {assessment_name}")
        params = {
            "course_name": course_name,
            "assessment_name": assessment_name
        }
        return self.make_api_request("GET", "/api/ubcseit/assessment_submissions", params)

    def get_course_sections(self, course_name: str) -> dict:
        # Returns all the course sections stored in the database for a given course. Not cached!
        # Note that students may be assigned to sections that don't exist in the database. This won't return those.
        # Returns a dict like:
        # {"course_display_name": "Some Course",
        #  "course_name": "somecourse",
        #  "sections": [{"days_code": 42,
        #                "end_time": "15:00:00",
        #                "is_lecture": True,
        #                "name": "A",
        #                "start_time": "13:00:00"},...
        #              ]
        # }
        # Sections are sorted alphabetically by name.
        logger.info(f"Getting Autolab sections for course {course_name}")
        params = {
            "course_name": course_name
        }
        return self.make_api_request("GET", "/api/ubcseit/course_sections/", params)

    def upsert_course_sections(self, course_name, sections: List[Dict[str, any]]) -> dict:
        # Create or update course sections for a given course.
        # Each section is uniquely identified by section_name, and is_lecture.
        # sections is a list of dicts like:
        # [
        #     {
        #         "days_code": 42,
        #         "start_time": "13:00:00",
        #         "end_time": "16:00:00",
        #         "name": "Auto1",
        #         "is_lecture": False,
        #     },...
        # ]
        # Returns a dict like:
        # {"course_display_name": "local", "course_name": "local", "success": True}
        logger.info(f"Upserting Autolab sections for course {course_name}, {sections}")
        params = {
            "course_name": course_name,
        }
        data = {
            "sections": sections
        }
        return self.make_api_request("POST", "/api/ubcseit/course_sections/", params, json=data)
