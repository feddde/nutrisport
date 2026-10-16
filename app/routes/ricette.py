from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Alimento, Ricetta, RicettaIngrediente
from app.schemas import IngredienteIn, RicettaCreate, RicettaOut, RicettaUpdate

router = APIRouter(prefix="/ricette", tags=["ricette"])


def _get_or_404(db: Session, ricetta_id: int) -> Ricetta:
    stmt = (
        select(Ricetta)
        .where(Ricetta.id == ricetta_id)
        .options(selectinload(Ricetta.ingredienti).selectinload(RicettaIngrediente.alimento))
    )
    ricetta = db.scalars(stmt).first()
    if ricetta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ricetta non trovata")
    return ricetta


def _costruisci_ingredienti(
    db: Session, ingredienti: list[IngredienteIn]
) -> list[RicettaIngrediente]:
    ids = [i.alimento_id for i in ingredienti]
    if len(set(ids)) != len(ids):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Alimento ripetuto: somma i grammi in un'unica riga",
        )
    trovati = set(db.scalars(select(Alimento.id).where(Alimento.id.in_(ids))))
    mancanti = sorted(set(ids) - trovati)
    if mancanti:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Alimenti non trovati: {mancanti}"
        )
    return [
        RicettaIngrediente(alimento_id=i.alimento_id, grammi=i.grammi)
        for i in ingredienti
    ]


@router.get("", response_model=list[RicettaOut])
def lista_ricette(q: str | None = None, db: Session = Depends(get_db)):
    stmt = (
        select(Ricetta)
        .order_by(Ricetta.nome)
        .options(selectinload(Ricetta.ingredienti).selectinload(RicettaIngrediente.alimento))
    )
    if q:
        stmt = stmt.where(Ricetta.nome.ilike(f"%{q}%"))
    return db.scalars(stmt).all()


@router.get("/{ricetta_id}", response_model=RicettaOut)
def leggi_ricetta(ricetta_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, ricetta_id)


@router.post("", response_model=RicettaOut, status_code=status.HTTP_201_CREATED)
def crea_ricetta(dati: RicettaCreate, db: Session = Depends(get_db)):
    ricetta = Ricetta(nome=dati.nome, istruzioni=dati.istruzioni)
    ricetta.ingredienti = _costruisci_ingredienti(db, dati.ingredienti)
    db.add(ricetta)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Esiste già una ricetta con questo nome")
    return _get_or_404(db, ricetta.id)


@router.patch("/{ricetta_id}", response_model=RicettaOut)
def modifica_ricetta(
    ricetta_id: int, dati: RicettaUpdate, db: Session = Depends(get_db)
):
    ricetta = _get_or_404(db, ricetta_id)
    campi = dati.model_dump(exclude_unset=True)
    if "nome" in campi and campi["nome"] is not None:
        ricetta.nome = campi["nome"]
    if "istruzioni" in campi:
        ricetta.istruzioni = campi["istruzioni"]
    if dati.ingredienti is not None:
        nuovi = _costruisci_ingredienti(db, dati.ingredienti)
        ricetta.ingredienti.clear()
        db.flush()
        ricetta.ingredienti.extend(nuovi)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Esiste già una ricetta con questo nome")
    db.expire_all()
    return _get_or_404(db, ricetta_id)


@router.delete("/{ricetta_id}", status_code=status.HTTP_204_NO_CONTENT)
def elimina_ricetta(ricetta_id: int, db: Session = Depends(get_db)):
    ricetta = _get_or_404(db, ricetta_id)
    db.delete(ricetta)
    db.commit()
