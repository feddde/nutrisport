import csv
from pathlib import Path

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Alimento

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "alimenti.csv"


def seed_alimenti(db) -> tuple[int, int]:
    """Inserisce gli alimenti dal CSV. Restituisce (inseriti, già presenti)."""
    esistenti = set(db.scalars(select(Alimento.nome)))
    inseriti = 0
    saltati = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for riga in csv.DictReader(f):
            nome = riga["nome"].strip()
            if nome in esistenti:
                saltati += 1
                continue
            db.add(
                Alimento(
                    nome=nome,
                    kcal=float(riga["kcal"]),
                    proteine=float(riga["proteine"]),
                    carboidrati=float(riga["carboidrati"]),
                    grassi=float(riga["grassi"]),
                )
            )
            esistenti.add(nome)
            inseriti += 1

    db.commit()
    return inseriti, saltati


def main() -> None:
    with SessionLocal() as db:
        inseriti, saltati = seed_alimenti(db)
    print(f"Alimenti inseriti: {inseriti}, già presenti: {saltati}")


if __name__ == "__main__":
    main()
