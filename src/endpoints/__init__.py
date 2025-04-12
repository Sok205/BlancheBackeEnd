from fastapi import APIRouter
from .registration import router as registration_router

router = APIRouter()
router.include_router(registration_router, tags=["users"])