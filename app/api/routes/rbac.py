from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clerk.auth import require_permission
from app.crud import rbac as rbac_crud
from app.db.session import get_db
from app.schemas.rbac import PermissionResponse, RoleCreate, RolePermissionsUpdate, RoleResponse, RoleUpdate

router = APIRouter()


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("role:read")),
):
    return rbac_crud.get_permissions(db)


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("role:read")),
):
    return rbac_crud.get_roles(db)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("role:create")),
):
    key = rbac_crud.slugify_role_key(payload.key or payload.name)
    if not key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role key cannot be empty")

    if key == "user":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'user' is the default public role")

    if rbac_crud.get_role_by_key(db, key) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")

    try:
        return rbac_crud.create_role(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists") from exc


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("role:read")),
):
    role = rbac_crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("role:update_permissions")),
):
    role = rbac_crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return rbac_crud.update_role(db, role, payload)


@router.put("/roles/{role_id}/permissions", response_model=RoleResponse)
def update_role_permissions(
    role_id: int,
    payload: RolePermissionsUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("role:update_permissions")),
):
    role = rbac_crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    try:
        return rbac_crud.update_role_permissions(db, role, payload.permission_keys)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_permission("role:update_permissions")),
):
    role = rbac_crud.get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if role.is_system:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="System roles cannot be deleted")

    rbac_crud.delete_role(db, role)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
