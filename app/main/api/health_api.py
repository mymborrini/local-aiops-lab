from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["HealthCheck"])


@router.get("")
def health_endpoint():
    return {"status": "UP"}
