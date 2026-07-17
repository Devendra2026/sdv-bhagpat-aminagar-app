from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.clerk.webhook import handle_clerk_webhook
from app.db.session import get_db

router = APIRouter()


@router.post("/webhooks", status_code=status.HTTP_200_OK)
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    return await handle_clerk_webhook(request, db)
