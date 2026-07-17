from fastapi import APIRouter,Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import Users
from app.schemas.user import UserUpdate, UserResponse
from app.db.session import get_db

router = APIRouter()

# get all the users
@router.get("",response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    return list(db.scalars(select(Users).order_by(Users.id.desc())))

# get user by id
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return user

# put is handled by clerk webhook

#update user by id
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int,payload:UserUpdate, db: Session = Depends(get_db)):
    user = db.get(Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    for field, value in payload.model_dump().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

#delete by id
@router.delete("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id:int, db:Session=Depends(get_db)):
    user = db.get(Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
