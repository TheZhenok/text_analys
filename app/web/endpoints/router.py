from fastapi.routing import APIRouter

from app.web.endpoints import text

api_router = APIRouter()
api_router.include_router(text.router, prefix="/text", tags=["user"])