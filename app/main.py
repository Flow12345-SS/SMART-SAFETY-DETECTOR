from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router as api_router
import os

app = FastAPI(
    title="Smart Safety Detector",
    description="Real-Time Workplace Safety Detection API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api")

# Mount Static Files (Frontend)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join("app", "static", "index.html"))

@app.get("/{catchall:path}")
def serve_frontend_pages(catchall: str):
    # Quick fix for SPA routing
    if os.path.exists(os.path.join("app", "static", f"{catchall}.html")):
        return FileResponse(os.path.join("app", "static", f"{catchall}.html"))
    return FileResponse(os.path.join("app", "static", "index.html"))
