from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError

from app.core.config import settings
from app.crud.user import create_user_from_clerk


async def handle_clerk_webhook(request: Request, db: Session) -> dict[str, str]:
    if not settings.clerk_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLERK_WEBHOOK_SECRET is not configured",
        )

    payload = await request.body()
    headers = {
        "svix-id": request.headers.get("svix-id", ""),
        "svix-timestamp": request.headers.get("svix-timestamp", ""),
        "svix-signature": request.headers.get("svix-signature", ""),
    }

    try:
        event = Webhook(settings.clerk_webhook_secret).verify(payload, headers)
    except WebhookVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Clerk webhook signature",
        )

    event_type = event.get("type")
    if event_type != "user.created":
        return {"message": "Event ignored"}

    user_data = event.get("data", {})
    clerk_id = user_data.get("id")
    email = _primary_email(user_data)
    name = _full_name(user_data)

    if not clerk_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clerk user.created payload is missing id or email",
        )

    create_user_from_clerk(
        db,
        clerk_id=clerk_id,
        email=email,
        name=name,
    )

    return {"message": "User stored successfully"}


def _primary_email(user_data: dict[str, Any]) -> str | None:
    email_addresses = user_data.get("email_addresses", [])
    primary_email_id = user_data.get("primary_email_address_id")

    for email_data in email_addresses:
        if email_data.get("id") == primary_email_id:
            return email_data.get("email_address")

    if email_addresses:
        return email_addresses[0].get("email_address")

    return None


def _full_name(user_data: dict[str, Any]) -> str:
    first_name = user_data.get("first_name") or ""
    last_name = user_data.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip()

    return full_name or "Unnamed User"
