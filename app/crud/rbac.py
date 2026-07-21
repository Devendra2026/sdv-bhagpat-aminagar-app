import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Permission, Role
from app.schemas.rbac import RoleCreate, RoleUpdate


DEFAULT_PERMISSIONS = [
    {
        "key": "contact:read",
        "label": "View contacts",
        "group": "Contact Submissions",
        "description": "Can view contact form submissions.",
    },
    {
        "key": "contact:update",
        "label": "Update contact status",
        "group": "Contact Submissions",
        "description": "Can update contact form records and status.",
    },
    {
        "key": "contact:delete",
        "label": "Delete contacts",
        "group": "Contact Submissions",
        "description": "Can delete contact form submissions.",
    },
    {
        "key": "grievance:read",
        "label": "View grievances",
        "group": "Public Grievances",
        "description": "Can view public grievance submissions.",
    },
    {
        "key": "grievance:update",
        "label": "Update grievance status",
        "group": "Public Grievances",
        "description": "Can update grievance records and status.",
    },
    {
        "key": "grievance:delete",
        "label": "Delete grievances",
        "group": "Public Grievances",
        "description": "Can delete grievance submissions.",
    },
    {
        "key": "user:read",
        "label": "View signed-up users",
        "group": "Users",
        "description": "Can view users created through Clerk signup/webhook.",
    },
    {
        "key": "user:update",
        "label": "Update users",
        "group": "Users",
        "description": "Can update user names and assign roles.",
    },
    {
        "key": "user:delete",
        "label": "Delete users",
        "group": "Users",
        "description": "Can delete signed-up users from the local database.",
    },
    {
        "key": "role:read",
        "label": "View roles",
        "group": "Roles & Permissions",
        "description": "Can view roles and allocated permissions.",
    },
    {
        "key": "role:create",
        "label": "Create roles",
        "group": "Roles & Permissions",
        "description": "Can create custom staff roles.",
    },
    {
        "key": "role:update_permissions",
        "label": "Edit role permissions",
        "group": "Roles & Permissions",
        "description": "Can change permissions assigned to roles.",
    },
]

DEFAULT_ROLES = [
    {
        "key": "admin",
        "name": "Administrator",
        "description": "Full system access.",
        "permissions": [permission["key"] for permission in DEFAULT_PERMISSIONS],
    },
    {
        "key": "head_clerk",
        "name": "Head Clerk",
        "description": "Can review and update contacts and grievances.",
        "permissions": [
            "contact:read",
            "contact:update",
            "grievance:read",
            "grievance:update",
            "user:read",
            "role:read",
        ],
    },
    {
        "key": "computer_operator",
        "name": "Computer Operator",
        "description": "Can view operational submissions.",
        "permissions": ["contact:read", "grievance:read"],
    },
]


def slugify_role_key(value: str) -> str:
    return re.sub(r"(^_+|_+$)", "", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip()


def get_permissions(db: Session) -> list[Permission]:
    return list(db.scalars(select(Permission).order_by(Permission.group, Permission.key)))


def get_permission_by_key(db: Session, key: str) -> Permission | None:
    return db.scalar(select(Permission).where(Permission.key == key))


def get_roles(db: Session) -> list[Role]:
    return list(db.scalars(select(Role).order_by(Role.is_system.desc(), Role.id)))


def get_role(db: Session, role_id: int) -> Role | None:
    return db.get(Role, role_id)


def get_role_by_key(db: Session, key: str) -> Role | None:
    return db.scalar(select(Role).where(Role.key == key))


def create_role(db: Session, payload: RoleCreate) -> Role:
    key = slugify_role_key(payload.key or payload.name)
    role = Role(
        key=key,
        name=payload.name,
        description=payload.description,
        is_system=False,
    )
    role.permissions = permissions_from_keys(db, payload.permission_keys)

    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role: Role, payload: RoleUpdate) -> Role:
    role.name = payload.name
    role.description = payload.description
    db.commit()
    db.refresh(role)
    return role


def update_role_permissions(db: Session, role: Role, permission_keys: list[str]) -> Role:
    role.permissions = permissions_from_keys(db, permission_keys)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: Role) -> None:
    db.delete(role)
    db.commit()


def permissions_from_keys(db: Session, permission_keys: list[str]) -> list[Permission]:
    if not permission_keys:
        return []

    permissions = list(db.scalars(select(Permission).where(Permission.key.in_(permission_keys))))
    found_keys = {permission.key for permission in permissions}
    missing_keys = set(permission_keys) - found_keys
    if missing_keys:
        raise ValueError(f"Unknown permission keys: {', '.join(sorted(missing_keys))}")

    return permissions


def seed_default_rbac(db: Session) -> None:
    for permission_data in DEFAULT_PERMISSIONS:
        permission = get_permission_by_key(db, permission_data["key"])
        if permission is None:
            db.add(Permission(**permission_data))
        else:
            permission.label = permission_data["label"]
            permission.group = permission_data["group"]
            permission.description = permission_data["description"]

    db.commit()

    for role_data in DEFAULT_ROLES:
        role = get_role_by_key(db, role_data["key"])
        if role is None:
            role = Role(
                key=role_data["key"],
                name=role_data["name"],
                description=role_data["description"],
                is_system=True,
            )
            db.add(role)
        else:
            role.name = role_data["name"]
            role.description = role_data["description"]
            role.is_system = True

        role.permissions = permissions_from_keys(db, role_data["permissions"])

    db.commit()
