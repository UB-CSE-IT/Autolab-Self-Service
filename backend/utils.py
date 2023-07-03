import hashlib
import logging
import os
import secrets

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
