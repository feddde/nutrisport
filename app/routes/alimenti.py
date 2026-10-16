from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alimento
from app.schemas import AlimentoCreate, AlimentoOut, AlimentoUpdate

router = APIRouter(prefix="/alimenti", tags=["alimenti"])


def _get_or_404(db: Session, alimento_id: int) -> Alimento:
    alimento = db.get(Alimento, alimento_id)
    if alimento is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alimento non trovato")
    return alimento


@router.get("", response_model=list[AlimentoOut])
def lista_alimenti(q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Alimento).order_by(Alimento.nome)
    if q:
        stmt = stmt.where(Alimento.nome.ilike(f"%{q}%"))
    return db.scalars(stmt).all()


@router.get("/{alimento_id}", response_model=AlimentoOut)
def leggi_alimento(alimento_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, alimento_id)


@router.post("", response_model=AlimentoOut, status_code=status.HTTP_201_CREATED)
def crea_alimento(dati: AlimentoCreate, db: Session = Depends(get_db)):
    alimento = Alimento(**dati.model_dump())
    db.add(alimento)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Esiste già un alimento con questo nome")
    db.refresh(alimento)
    return alimento


@router.patch("/{alimento_id}", response_model=AlimentoOut)
def modifica_alimento(
    alimento_id: int, dati: AlimentoUpdate, db: Session = Depends(get_db)
):
    alimento = _get_or_404(db, alimento_id)
    for campo, valore in dati.model_dump(exclude_unset=True).items():
        setattr(alimento, campo, valore)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Esiste già un alimento con questo nome")
    db.refresh(alimento)
    return alimento


@router.delete("/{alimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def elimina_alimento(alimento_id: int, db: Session = Depends(get_db)):
    alimento = _get_or_404(db, alimento_id)
    db.delete(alimento)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Alimento usato in ricette o nel diario: non eliminabile",
        )
