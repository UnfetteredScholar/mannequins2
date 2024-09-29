from core.config import settings
from fastapi import APIRouter
from fastapi.responses import Response
from schemas.health import Health, Status

router = APIRouter()


class HealthResponse(Response):
    media_type = "application/health+json"


@router.get(
    path="/health", response_model=Health, response_class=HealthResponse
)
def get_health(response: HealthResponse):
    """Gets the health of the API"""
    response.headers["Cache-Control"] = "max-age=3600"

    content = {
        "status": Status.PASS,
        "version": settings.version,
        "releaseId": settings.releaseId,
    }

    return content
