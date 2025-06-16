from fastapi import APIRouter

router = APIRouter()

@router.get("/health-check", tags=["Health"])
async def health_check():
    """
    Vérifie la disponibilité de l'API.
    """
    return {"status": "ok", "message": "L'API est disponible"}
