"""The browser needs the server's VAPID *public* key to create a push subscription.
Rather than asking you to configure a second env var that must match the private key,
we derive it from VAPID_PRIVATE_KEY (or use VAPID_PUBLIC_KEY if you set it explicitly)."""
import base64
import logging
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


@lru_cache(maxsize=4)
def _derive_public_key(private_key: str) -> str:
    from cryptography.hazmat.primitives import serialization
    from py_vapid import Vapid

    key = private_key.strip()
    vapid = Vapid.from_pem(key.encode()) if "BEGIN" in key else Vapid.from_string(key)
    raw = vapid.public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    return _b64url(raw)


def get_public_key() -> str:
    """Base64url public key for `applicationServerKey`, or '' if push isn't configured."""
    if settings.vapid_public_key.strip():
        return settings.vapid_public_key.strip()
    if not settings.vapid_private_key.strip():
        return ""
    try:
        return _derive_public_key(settings.vapid_private_key)
    except Exception:
        logger.exception("Could not derive the VAPID public key from VAPID_PRIVATE_KEY")
        return ""
