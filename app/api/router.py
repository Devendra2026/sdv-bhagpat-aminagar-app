from fastapi import APIRouter

from app.api.routes import clerk, contact, grievance, user

api_router = APIRouter()
api_router.include_router(clerk.router, prefix="/clerk", tags=["Clerk"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(grievance.router, prefix="/grievance", tags=["Grievance"])
api_router.include_router(user.router,prefix="/user",tags=["User"])
