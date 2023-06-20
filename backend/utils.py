import hashlib
import secrets


def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_random_string(length: int = 256) -> str:
    # Note that the length of the returned string is longer than the input length because of the base64 encoding
    return secrets.token_urlsafe(length)
