from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers.root_app import router as root_router
from app.routers.health_check import router as health_check_router
import logging
import uvicorn


# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gestion des Packing Lists API",
    description="API pour gérer et traiter les Packing Lists des fournisseurs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware CORS pour gérer les requêtes externes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du routeur unique pour tous les fournisseurs
app.include_router(root_router, prefix="/api", tags=["Fournisseurs"])
app.include_router(health_check_router, prefix="/api", tags=["Health"])

@app.get("/")
def root():
    return {"message": "Bienvenue dans l'API de gestion des Packing Lists"}