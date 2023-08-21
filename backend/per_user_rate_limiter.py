from datetime import datetime
from collections import deque
from functools import wraps
from typing import Dict

from flask import g, jsonify


class PerUserRateLimiter:
    def __init__(self, times_per_period: int, seconds: float):
        # To limit to 5 requests per 10 seconds, use RateLimiter(5, 10)
        self.times_per_period = times_per_period
        self.seconds = seconds
        self.__users: Dict[str, deque] = {}

    def __repr__(self):
        return f"<RateLimiter {self.times_per_period} times per {self.seconds} seconds>"

    def update_to_current_time(self, current_time: datetime, user_queue: deque):
        # Gets a given queue into the correct state for the current time to begin checks
        # Removes all access times that are older than the current time minus the period
        # Pass a current time so that the time used is consistent across all methods
        while len(user_queue) > 0 and (current_time - user_queue[0]).total_seconds() > self.seconds:
            user_queue.popleft()

    def try_use(self, username: str):
        # Returns True if the user is allowed access at this time, False otherwise
        # Adds the current time to the user's queue if they are allowed access
        if username not in self.__users:
            self.__users[username] = deque()
        user_queue = self.__users[username]
        now = datetime.now()
        self.update_to_current_time(now, user_queue)
        if len(user_queue) < self.times_per_period:
            user_queue.append(now)
            return True
        return False

    def get_remaining_time(self, username: str) -> float:
        # Return the number of seconds remaining until the given user can perform an action again
        # Returns 0.0 if the user can perform an action now
        if username not in self.__users:
            return 0.0
        user_queue = self.__users[username]
        now = datetime.now()
        self.update_to_current_time(now, user_queue)
        if len(user_queue) < self.times_per_period:
            return 0.0
        return max(self.seconds - (now - user_queue[0]).total_seconds(), 0.0)

    @staticmethod
    def human_readable_seconds(seconds: float) -> str:
        # Returns a human-readable string of the given number of seconds

        if seconds > 10.0:
            return "{0:.0f} seconds".format(seconds)
        elif seconds > 1.2:
            return "{0:.1f} seconds".format(seconds)
        else:
            return "a second"


# A Flask decorator that limits the number of requests a user can make to a given endpoint
# Important: It must go UNDER the @app route decorator

# Example Usage:
# @app.api.route("/path/", methods=["POST"])
# @rate_limit_per_user(2, 5)  # Limit to 2 requests per 5 seconds
# def some_view():

# They can be combined to have low frequency limits and high frequency limits
# Important: Put the low frequency limit first, otherwise the remaining time the
# user sees in the error will be incorrect
# Example Usage:
# @app.api.route("/path/", methods=["POST"])
# @rate_limit_per_user(3, 20)  # Limit to 3 requests per 20 seconds
# @rate_limit_per_user(1, 3)  # And also limit to 1 request per 3 seconds to prevent short bursts
# def some_view():

def rate_limit_per_user(times_per_period: int, seconds: float):
    def decorator(func):
        limiter = PerUserRateLimiter(times_per_period, seconds)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.user is None:
                return jsonify({
                    "success": False,
                    "error": "You are not logged in."
                }), 401

            if not limiter.try_use(g.user.username):
                remaining_time: str = PerUserRateLimiter.human_readable_seconds(
                    limiter.get_remaining_time(g.user.username))
                resp = jsonify({
                    "success": False,
                    "error": f"You've exceeded your rate limit. You'll need to wait {remaining_time} before trying"
                             " that again."
                })
                return resp, 429
            return func(*args, **kwargs)

        return wrapper

    return decorator
