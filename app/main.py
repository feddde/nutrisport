from fastapi import FastAPI

from app.routes import alimenti

app = FastAPI(title="NutriSport")
app.include_router(alimenti.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
