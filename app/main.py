from fastapi import FastAPI

app = FastAPI(title="NutriSport")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
