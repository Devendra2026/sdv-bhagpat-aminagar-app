from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_clerk_id(db: Session, clerk_id: str) -> User | None:
    return db.scalar(select(User).where(User.clerk_id == clerk_id))


def create_user_from_clerk(
    db: Session,
    *,
    clerk_id: str,
    email: str,
    name: str,
) -> User:
    existing_user = get_user_by_clerk_id(db, clerk_id)
    if existing_user is not None:
        return existing_user

    user = User(
        clerk_id=clerk_id,
        email=email,
        name=name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
