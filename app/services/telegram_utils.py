from typing import Optional


def telegram_display_name(user: Optional[dict]) -> Optional[str]:
    """Readable label for a Telegram user: @username, else first/last name, else None."""
    if not user:
        return None
    if user.get("username"):
        return f"@{user['username']}"
    full = " ".join(p for p in (user.get("first_name"), user.get("last_name")) if p)
    return full or None
