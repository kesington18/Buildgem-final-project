"""Create an admin account, or promote an existing user to admin.

    python -m app.scripts.create_admin --email admin@school.edu --name "Site Admin"
    python -m app.scripts.create_admin --email admin@school.edu --reset-password

New account: you are prompted for a password (never passed on the command line).
Existing account: it is promoted to admin and its password is KEPT, unless you add
--reset-password, which prompts for a new one.
Public registration only ever creates students, so this is the one way to get an admin.
"""
import argparse
import getpass
import sys

from app.core.security import hash_password
from app.db.session import sessionLocal
from app.models.user import User, UserRole


def _ask_password() -> str | None:
    password = getpass.getpass("Password (min 8 chars): ")
    if len(password) < 8:
        print("Password too short.", file=sys.stderr)
        return None
    return password


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="Admin")
    parser.add_argument("--reset-password", action="store_true",
                        help="set a new password even if the account already exists")
    args = parser.parse_args()
    email = args.email.strip().lower()

    db = sessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = UserRole.admin
            message = f"Promoted existing user {email} to admin (password unchanged)."
            if args.reset_password:
                password = _ask_password()
                if password is None:
                    return 1
                user.password_hash = hash_password(password)
                message = f"Promoted {email} to admin and set a new password."
            db.commit()
            print(message)
            return 0

        password = _ask_password()
        if password is None:
            return 1
        db.add(User(name=args.name, email=email, password_hash=hash_password(password), role=UserRole.admin))
        db.commit()
        print(f"Created admin {email}.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
