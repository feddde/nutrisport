import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Alimento, Ricetta, RicettaIngrediente


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


def test_ricetta_con_due_ingredienti(db):
    riso = Alimento(nome="Riso", kcal=350, proteine=8, carboidrati=77, grassi=0.6)
    pollo = Alimento(nome="Pollo", kcal=110, proteine=23, carboidrati=0, grassi=1.2)
    ricetta = Ricetta(nome="Riso e pollo")
    ricetta.ingredienti = [
        RicettaIngrediente(alimento=riso, grammi=80),
        RicettaIngrediente(alimento=pollo, grammi=150),
    ]
    db.add(ricetta)
    db.commit()

    salvata = db.query(Ricetta).filter_by(nome="Riso e pollo").one()
    assert len(salvata.ingredienti) == 2
    assert {i.alimento.nome for i in salvata.ingredienti} == {"Riso", "Pollo"}
    assert sum(i.grammi for i in salvata.ingredienti) == 230


def test_valori_negativi_rifiutati(db):
    db.add(Alimento(nome="Errore", kcal=-1, proteine=0, carboidrati=0, grassi=0))
    with pytest.raises(IntegrityError):
        db.commit()


def test_alimento_in_uso_non_eliminabile(db):
    riso = Alimento(nome="Riso", kcal=350, proteine=8, carboidrati=77, grassi=0.6)
    ricetta = Ricetta(nome="Riso in bianco")
    ricetta.ingredienti = [RicettaIngrediente(alimento=riso, grammi=100)]
    db.add(ricetta)
    db.commit()

    db.delete(riso)
    with pytest.raises(IntegrityError):
        db.commit()
