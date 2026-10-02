import getpass

from app.db.session import sessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


def create_admin():
    db = sessionLocal()
    try:
        name = input("Name: ").strip()
        email = input("Email: ").strip().lower()
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("Passwords do not match.")
            return

        if db.query(User).filter(User.email == email).first():
            print(f"A user with email {email} already exists.")
            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        print(f"Admin account created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()