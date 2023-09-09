import hashlib
import logging
import os
import secrets
import time

logger = logging.getLogger("portal")


def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_random_string(length: int = 256) -> str:
    # Note that the length of the returned string is longer than the input length because of the base64 encoding
    return secrets.token_urlsafe(length)


def get_client_ip(request):
    # This will correctly return the client's actual IP address based on the X-Forwarded-For header
    # This is ordinarily easily spoofed, so the NUM_PROXIES environment variable must be set accurately.
    # I.e., if the configuration is Apache -> Nginx -> App, then NUM_PROXIES=2
    # If you're running the app locally without a proxy, NUM_PROXIES=0
    num_proxies = int(os.getenv("NUM_PROXIES", 0))
    if num_proxies == 0:
        return request.remote_addr
    try:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        return x_forwarded_for.split(",")[-num_proxies].strip()
    except (IndexError, AttributeError):
        logger.error("X-Forwarded-For header is malformed or missing. Verify NUM_PROXIES is set correctly. "
                     "Using remote_addr for IP instead, which may not be accurate.")
        return request.remote_addr


def class_meeting_pattern_source_key_to_days_code(class_meeting_pattern_source_key: str) -> int:
    # Converts something like "MWF" to 42
    day_values = {
        "U": 1,  # (Sunday doesn't seem to exist in InfoSource)
        "M": 2,
        "T": 4,
        "W": 8,
        "R": 16,
        "F": 32,
        "S": 64,
    }
    days_code: int = 0
    try:
        for day in class_meeting_pattern_source_key:
            days_code += day_values[day]
    except KeyError:
        return 0

    return days_code


def twelve_hour_time_to_24_hour_time(twelve_hour_time: str) -> str:
    # Converts something like "5:00PM" to "17:00:00"
    return time.strftime("%H:%M:%S", time.strptime(twelve_hour_time, "%I:%M%p"))
