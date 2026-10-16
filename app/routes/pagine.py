from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alimento

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


@router.get("/alimenti-pagina", response_class=HTMLResponse)
def pagina_alimenti(request: Request, db: Session = Depends(get_db)):
    alimenti = db.scalars(select(Alimento).order_by(Alimento.nome)).all()
    return templates.TemplateResponse(
        request, "alimenti.html", {"alimenti": alimenti}
    )
