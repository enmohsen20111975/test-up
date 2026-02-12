from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from database import engine, Base, get_db
from workflow_database import workflow_engine, WorkflowBase, get_workflow_db
from config import settings
import logging
import os
import json
from typing import Dict

# Import models to ensure they're registered with Base
from auth.models import User, CalculationHistory, WorkflowHistory, SubscriptionHistory
from workflow_models import (
    Equation, EquationCategory, EquationInput, EquationOutput, 
    EquationUnit, EquationExample,
    Workflow, WorkflowCategory, WorkflowInput, WorkflowOutput, WorkflowStep
)

# Create tables in user database
print("Creating user database tables...")
Base.metadata.create_all(bind=engine)
print("User database tables created successfully!")

# Create tables in workflow database
print("Creating workflow database tables...")
WorkflowBase.metadata.create_all(bind=workflow_engine)
print("Workflow database tables created successfully!")

# Note: Workflows and equations should be migrated using the migration script
# Run: python backend/migrate_workflow_database.py

# Initialize FastAPI
app = FastAPI(
    title="EngiSuite Analytics Pro",
    description="Unified SaaS platform for engineering calculations and data analysis",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Internationalization (i18n) Setup ---
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locales")
_translations: Dict[str, str] = {}

def load_translations(lang_code: str):
    global _translations
    lang_path = os.path.join(LOCALE_DIR, lang_code, "messages.json")
    if os.path.exists(lang_path):
        with open(lang_path, "r", encoding="utf-8") as f:
            _translations = json.load(f)
    else:
        _translations = {} # Fallback to empty if no translation file

def _(text: str) -> str:
    """Translation function."""
    return _translations.get(text, text)

@app.middleware("http")
async def add_i18n_middleware(request: Request, call_next):
    lang_code = request.query_params.get("lang") or request.headers.get("Accept-Language", "ar").split(',')[0].split('-')[0]
    
    # Validate language code
    if lang_code not in ["en", "ar", "fr"]: # Supported languages
        lang_code = "ar" # Default to Arabic

    load_translations(lang_code)
    response = await call_next(request)
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (must come before routers and static files)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Include routers
from auth.router import router as auth_router
from auth.google_oauth_routes import router as google_oauth_router
from calculators.router import router as calculators_router
from analytics.router import router as analytics_router
from ai.router import router as ai_router
from payments.router import router as payments_router
from workflows.router import router as workflows_router
from calculation_pipeline.router import router as calculation_pipeline_router

app.include_router(auth_router)
app.include_router(google_oauth_router)
app.include_router(calculators_router)
app.include_router(analytics_router)
app.include_router(ai_router)
app.include_router(payments_router)
app.include_router(workflows_router)
app.include_router(calculation_pipeline_router)

# Mount static files from frontend folder (must come last!)
from pathlib import Path
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    print(f"[OK] Mounted frontend folder: {frontend_path}")
else:
    print(f"[WARN] Warning: frontend folder not found at {frontend_path}")

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": _("Internal server error"), "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
