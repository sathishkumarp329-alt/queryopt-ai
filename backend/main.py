import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.api import analyze, query, history, reports, evaluation
from backend.database import init_app_db
from backend.config import settings
from database.init_db import init_database
import uvicorn

app = FastAPI(
    title="QueryOpt AI — Agentic SQL Query Analysis & Optimization",
    description="Production-style agentic AI workflow for SQL query analysis, performance detection, and safe optimization.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers first
app.include_router(analyze.router)
app.include_router(query.router)
app.include_router(history.router)
app.include_router(reports.router)
app.include_router(evaluation.router)

@app.on_event("startup")
def on_startup():
    # Initialize application metadata database
    init_app_db()
    
    # Initialize demo database if not present
    demo_db = Path(settings.DEMO_DB_PATH)
    if not demo_db.exists() or demo_db.stat().st_size == 0:
        print("[Startup] Initializing demo SQLite database...")
        init_database(str(demo_db))

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": "QueryOpt AI",
        "version": "1.0.0",
        "demo_database": "connected"
    }

# Check for production frontend build (e.g. frontend/dist or static/)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
static_dist = Path(__file__).parent.parent / "static"

dist_path = frontend_dist if frontend_dist.exists() else (static_dist if static_dist.exists() else None)

if dist_path and dist_path.exists():
    assets_path = dist_path / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(request: Request, full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        
        file_candidate = dist_path / full_path
        if full_path and file_candidate.exists() and file_candidate.is_file():
            return FileResponse(file_candidate)
        
        index_html = dist_path / "index.html"
        if index_html.exists():
            return FileResponse(index_html)
        return JSONResponse(status_code=404, content={"detail": "index.html not found"})
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "message": "QueryOpt AI Backend API running in development mode.",
            "docs": "/docs",
            "health": "/api/health"
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
