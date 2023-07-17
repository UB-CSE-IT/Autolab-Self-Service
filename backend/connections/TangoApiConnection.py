import datetime
import logging
import math
import threading
from typing import List

import requests

logger = logging.getLogger("portal")


class TangoApiConnection:

    def __init__(self, tango_host: str, tango_key: str, tango_max_poll_rate: float):
        self.__tango_host = tango_host
        self.__tango_key = tango_key
        self.__tango_max_poll_rate = tango_max_poll_rate
        self.last_fetch_time = datetime.datetime(1970, 1, 1)
        self.raw_data_cache = {}
        self.update_lock = threading.Lock()

    def __get_raw_job_data(self) -> dict:
        # This data contains sensitive information, such as email addresses and the Tango API key.
        # Don't share the raw data.
        with self.update_lock:
            if self.last_fetch_time + datetime.timedelta(seconds=self.__tango_max_poll_rate) < datetime.datetime.now():
                self.last_fetch_time = datetime.datetime.now()
                self.raw_data_cache["dead_jobs"] = \
                    requests.get(f"{self.__tango_host}/jobs/{self.__tango_key}/1/").json()
                self.raw_data_cache["current_jobs"] = \
                    requests.get(f"{self.__tango_host}/jobs/{self.__tango_key}/0/").json()
        return self.raw_data_cache

    def __get_combined_jobs(self) -> List[dict]:
        # Return a list of running and finished ("dead") jobs
        # This still contains sensitive information.
        data = self.__get_raw_job_data()
        return data.get("dead_jobs").get("jobs") + data.get("current_jobs").get("jobs")

    def get_recent_submission_times(self) -> List[datetime.datetime]:
        jobs: List[dict] = self.__get_combined_jobs()
        job: dict
        start_times: List[datetime.datetime] = []
        for job in jobs:
            try:
                date_string = job.get("trace")[0].split("|")[0].strip()
                # Parse the date in this format: Sun Jul  9 20:57:31 2023
                date: datetime.datetime = datetime.datetime.strptime(date_string, "%a %b %d %H:%M:%S %Y") \
                    .replace(tzinfo=datetime.timezone.utc)
                start_times.append(date)
            except Exception:
                pass  # Just ignore this job. I don't know why it wouldn't have an entry, but it's not important.
        return start_times

    def get_recent_submissions_histogram(self) -> dict[int, int]:
        # Return a dict of seconds to number of submissions within the past key seconds
        # It's technically a cumulative histogram, not a regular one.

        submission_dates = self.get_recent_submission_times()
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        sample_seconds = [1, 2, 3, 5, 10, 15, 20, 30, 60, 120, 300, 600, 1800, 3600, 7200, 14400, 28800, 57600, 86400,
                          172800, 259200, 345600, 432000, 518400, 604800, 1209600, 2592000]

        histogram: dict[int, int] = {k: 0 for k in sample_seconds}

        for date in submission_dates:
            seconds_ago: float = (now - date).total_seconds()
            for seconds in sample_seconds:
                if seconds_ago < seconds:
                    histogram[seconds] += 1

        return histogram

    @staticmethod
    def annotate_time_histogram(histogram: dict[int, int]) -> dict[int, dict[str, any]]:
        # Annotate the histogram with a human-readable amount of time
        max_submissions = max(histogram.values())
        annotated_histogram: dict[int, dict[str, any]] = {}
        for seconds, submission_count in histogram.items():
            count = seconds
            unit = "second"
            if count >= 60:
                count /= 60
                unit = "minute"
                if count >= 60:
                    count /= 60
                    unit = "hour"
                    if count >= 24:
                        count /= 24
                        unit = "day"
            if count != 1:
                unit += "s"

            annotated_histogram[seconds] = {
                "count": submission_count,
                "timeframe": f"{int(count)} {unit}",
                "sentence": f"{submission_count} submission{'s' if submission_count != 1 else ''} "
                            f"in the past {int(count)} {unit}",
                "percent": math.ceil(submission_count / max_submissions * 100),
                "seconds": seconds,
            }

        return annotated_histogram
