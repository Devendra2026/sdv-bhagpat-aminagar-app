from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.grievance import Grievance
from app.schemas.grievance import GrievanceCreate, GrievanceUpdate


def create_grievance(db: Session, payload: GrievanceCreate) -> Grievance:
    grievance = Grievance(**payload.model_dump())
    db.add(grievance)
    db.commit()
    db.refresh(grievance)
    return grievance


def get_grievances(db: Session) -> list[Grievance]:
    return list(db.scalars(select(Grievance).order_by(Grievance.id.desc())))


def get_grievance(db: Session, grievance_id: int) -> Grievance | None:
    return db.get(Grievance, grievance_id)


def update_grievance(db: Session, grievance: Grievance, payload: GrievanceUpdate) -> Grievance:
    for field, value in payload.model_dump().items():
        setattr(grievance, field, value)

    db.commit()
    db.refresh(grievance)
    return grievance


def delete_grievance(db: Session, grievance: Grievance) -> None:
    db.delete(grievance)
    db.commit()
