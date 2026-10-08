"""Only real browser push services may be stored as a subscription endpoint.

Why this matters: the server POSTs to whatever URL is saved as `endpoint`. If any logged-in
user could save an arbitrary URL, they could make our server send requests to internal
addresses (SSRF). So we allow-list the push services the big browsers actually use.
"""
from urllib.parse import urlparse

ALLOWED_PUSH_HOSTS = (
    "fcm.googleapis.com",            # Chrome, Edge (Android), Opera, Samsung Internet, Brave
    "push.services.mozilla.com",     # Firefox
    "notify.windows.com",            # Edge on Windows (WNS)
    "push.apple.com",                # Safari / iOS web push
)


def is_allowed_push_endpoint(url: str) -> bool:
    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host or parsed.username or port not in (None, 443):
        return False
    return any(host == d or host.endswith("." + d) for d in ALLOWED_PUSH_HOSTS)
