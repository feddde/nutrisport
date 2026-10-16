from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Alimento
from app.schemas import AlimentoCreate, AlimentoUpdate

def get_alimenti(db: Session, skip: int = 0, limit: int = 100):
    stmt = select(Alimento).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())

def get_alimento(db: Session, alimento_id: int):
    return db.get(Alimento, alimento_id)

def create_alimento(db: Session, alimento: AlimentoCreate):
    db_alimento = Alimento(**alimento.model_dump())
    db.add(db_alimento)
    db.commit()
    db.refresh(db_alimento)
    return db_alimento

def update_alimento(db: Session, alimento_id: int, alimento_update: AlimentoUpdate):
    db_alimento = db.get(Alimento, alimento_id)
    if not db_alimento:
        return None
    
    update_data = alimento_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_alimento, key, value)
        
    db.commit()
    db.refresh(db_alimento)
    return db_alimento

def delete_alimento(db: Session, alimento_id: int):
    db_alimento = db.get(Alimento, alimento_id)
    if db_alimento:
        db.delete(db_alimento)
        db.commit()
        return True
    return False
