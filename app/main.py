from fastapi import FastAPI

from app.routes import alimenti, ricette

app = FastAPI(title="NutriSport")
app.include_router(alimenti.router)
app.include_router(ricette.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
