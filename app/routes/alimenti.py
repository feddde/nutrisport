from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/alimenti", tags=["alimenti"])

@router.post("/", response_model=schemas.AlimentoOut)
def create_alimento(alimento: schemas.AlimentoCreate, db: Session = Depends(get_db)):
    return crud.create_alimento(db=db, alimento=alimento)

@router.get("/", response_model=list[schemas.AlimentoOut])
def read_alimenti(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_alimenti(db, skip=skip, limit=limit)

@router.get("/{alimento_id}", response_model=schemas.AlimentoOut)
def read_alimento(alimento_id: int, db: Session = Depends(get_db)):
    db_alimento = crud.get_alimento(db, alimento_id=alimento_id)
    if db_alimento is None:
        raise HTTPException(status_code=404, detail="Alimento non trovato")
    return db_alimento
