from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.rbac import get_role_by_key
from app.crud.user import get_user_by_clerk_id
from app.db.session import get_db
from app.models.user import Users


bearer_scheme = HTTPBearer(auto_error=False)
_jwks_client: PyJWKClient | None = None


@dataclass
class CurrentUser:
    user: Users
    clerk_claims: dict[str, Any]
    permissions: set[str]

    @property
    def role(self) -> str:
        return self.user.role


def clerk_jwks_url() -> str:
    if settings.clerk_jwks_url:
        return settings.clerk_jwks_url

    if settings.clerk_issuer_url:
        return f"{settings.clerk_issuer_url.rstrip('/')}/.well-known/jwks.json"

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="CLERK_ISSUER_URL is not configured",
    )


def jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(clerk_jwks_url())
    return _jwks_client


def decode_clerk_token(token: str) -> dict[str, Any]:
    try:
        signing_key = jwks_client().get_signing_key_from_jwt(token)
        decode_kwargs: dict[str, Any] = {
            "key": signing_key.key,
            "algorithms": ["RS256"],
            "options": {"verify_aud": False},
        }
        if settings.clerk_issuer_url:
            decode_kwargs["issuer"] = settings.clerk_issuer_url.rstrip("/")

        return jwt.decode(token, **decode_kwargs)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Clerk token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def permissions_for_user(db: Session, user: Users) -> set[str]:
    if user.role == "user":
        return set()

    role = get_role_by_key(db, user.role)
    if role is None:
        return set()

    return {permission.key for permission in role.permissions}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = decode_clerk_token(credentials.credentials)
    clerk_id = claims.get("sub")
    if not isinstance(clerk_id, str) or not clerk_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Clerk token subject")

    user = get_user_by_clerk_id(db, clerk_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not registered in database")

    return CurrentUser(user=user, clerk_claims=claims, permissions=permissions_for_user(db, user))


def require_permission(permission: str):
    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if permission not in current_user.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return current_user

    return dependency
