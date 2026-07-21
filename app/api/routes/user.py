from fastapi import APIRouter,Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.clerk.auth import CurrentUser, get_current_user, require_permission
from app.crud.rbac import get_role_by_key
from app.models.user import Users
from app.schemas.user import UserUpdate, UserResponse
from app.db.session import get_db

router = APIRouter()


def ensure_assignable_role(db: Session, role: str) -> None:
    if role == "user":
        return

    if get_role_by_key(db, role) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role not found")

# get all the users
@router.get("",response_model=list[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("user:read")),
):
    return list(db.scalars(select(Users).order_by(Users.id.desc())))


@router.get("/me")
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    return {
        "id": current_user.user.id,
        "clerk_id": current_user.user.clerk_id,
        "email": current_user.user.email,
        "name": current_user.user.name,
        "role": current_user.user.role,
        "permissions": sorted(current_user.permissions),
        "created_at": current_user.user.created_at,
    }

# get user by id
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("user:read")),
):
    user = db.get(Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return user

# put is handled by clerk webhook

#update user by id
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload:UserUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("user:update")),
):
    user = db.get(Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    ensure_assignable_role(db, payload.role)

    for field, value in payload.model_dump().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("user:update")),
):
    user = db.get(Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    ensure_assignable_role(db, payload.role)

    user.name = payload.name
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user

#delete by id
@router.delete("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id:int,
    db:Session=Depends(get_db),
    _current_user=Depends(require_permission("user:delete")),
):
    user = db.get(Users, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
