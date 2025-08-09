from fastapi import FastAPI
from .api import routes

app = FastAPI(title="ClauseGPT - Intelligent Policy Query System", version="0.1.0")

app.include_router(routes.router)

@app.get("/health")
def health():
    return {"status": "ok"}
