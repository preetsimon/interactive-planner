from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.time_blocks import router as time_blocks_router
from app.api.v1.priorities import router as priorities_router
from app.api.v1.cadence import router as cadence_router
from app.api.v1.domains import router as domains_router
from app.api.v1.audits import router as audits_router
from app.api.v1.learning import router as learning_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(time_blocks_router)
api_router.include_router(priorities_router)
api_router.include_router(cadence_router)
api_router.include_router(domains_router)
api_router.include_router(audits_router)
api_router.include_router(learning_router)
