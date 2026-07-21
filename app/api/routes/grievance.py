from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.crud import grievance as grievance_crud
from app.clerk.auth import require_permission
from app.db.session import get_db
from app.schemas.grievance import GrievanceCreate, GrievanceResponse, GrievanceUpdate

router = APIRouter()


@router.post("", response_model=GrievanceResponse, status_code=status.HTTP_201_CREATED)
def create_grievance(payload: GrievanceCreate, db: Session = Depends(get_db)):
    return grievance_crud.create_grievance(db, payload)


@router.get("", response_model=list[GrievanceResponse])
def list_grievances(
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("grievance:read")),
):
    return grievance_crud.get_grievances(db)


@router.get("/{grievance_id}", response_model=GrievanceResponse)
def get_grievance(
    grievance_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("grievance:read")),
):
    grievance = grievance_crud.get_grievance(db, grievance_id)
    if grievance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grievance not found")
    return grievance


@router.put("/{grievance_id}", response_model=GrievanceResponse)
def update_grievance(
    grievance_id: int,
    payload: GrievanceUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("grievance:update")),
):
    grievance = grievance_crud.get_grievance(db, grievance_id)
    if grievance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grievance not found")
    return grievance_crud.update_grievance(db, grievance, payload)


@router.delete("/{grievance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grievance(
    grievance_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("grievance:delete")),
):
    grievance = grievance_crud.get_grievance(db, grievance_id)
    if grievance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grievance not found")

    grievance_crud.delete_grievance(db, grievance)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
