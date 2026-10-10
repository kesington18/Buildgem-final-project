"""Web-push key helper.

    python -m app.scripts.vapid_keys             # print the PUBLIC key for your current VAPID_PRIVATE_KEY
    python -m app.scripts.vapid_keys --generate  # make a brand-new key pair

You normally don't need this: the server derives the public key automatically.
Use --generate only if you have no VAPID key yet. Changing keys later invalidates every
existing push subscription (users just need to re-enable push).
"""
import base64
import sys


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def generate() -> int:
    from cryptography.hazmat.primitives import serialization
    from py_vapid import Vapid

    vapid = Vapid()
    vapid.generate_keys()
    private_raw = vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
    public_raw = vapid.public_key.public_bytes(
        encoding=serialization.Encoding.X962, format=serialization.PublicFormat.UncompressedPoint
    )
    print("VAPID_PRIVATE_KEY=" + _b64url(private_raw))
    print("VAPID_PUBLIC_KEY=" + _b64url(public_raw))
    return 0


def show_public() -> int:
    from app.core.vapid import get_public_key

    key = get_public_key()
    if not key:
        print("VAPID_PRIVATE_KEY is missing or unreadable.", file=sys.stderr)
        return 1
    print("VAPID_PUBLIC_KEY=" + key)
    return 0


if __name__ == "__main__":
    sys.exit(generate() if "--generate" in sys.argv else show_public())
