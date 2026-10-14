from datetime import date, time

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alimento(Base):
    __tablename__ = "alimenti"
    __table_args__ = (
        CheckConstraint("kcal >= 0", name="ck_alimento_kcal"),
        CheckConstraint("proteine >= 0", name="ck_alimento_proteine"),
        CheckConstraint("carboidrati >= 0", name="ck_alimento_carboidrati"),
        CheckConstraint("grassi >= 0", name="ck_alimento_grassi"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    # valori per 100 g
    kcal: Mapped[float]
    proteine: Mapped[float]
    carboidrati: Mapped[float]
    grassi: Mapped[float]


class Ricetta(Base):
    __tablename__ = "ricette"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
    istruzioni: Mapped[str | None]

    ingredienti: Mapped[list["RicettaIngrediente"]] = relationship(
        back_populates="ricetta", cascade="all, delete-orphan"
    )


class RicettaIngrediente(Base):
    __tablename__ = "ricetta_ingredienti"
    __table_args__ = (
        CheckConstraint("grammi > 0", name="ck_ingrediente_grammi"),
        UniqueConstraint("ricetta_id", "alimento_id", name="uq_ricetta_alimento"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ricetta_id: Mapped[int] = mapped_column(
        ForeignKey("ricette.id", ondelete="CASCADE")
    )
    alimento_id: Mapped[int] = mapped_column(
        ForeignKey("alimenti.id", ondelete="RESTRICT")
    )
    grammi: Mapped[float]

    ricetta: Mapped["Ricetta"] = relationship(back_populates="ingredienti")
    alimento: Mapped["Alimento"] = relationship()


class PianoPasto(Base):
    __tablename__ = "piano"
    __table_args__ = (
        CheckConstraint("giorno_settimana BETWEEN 0 AND 6", name="ck_piano_giorno"),
        CheckConstraint("opzione BETWEEN 1 AND 3", name="ck_piano_opzione"),
        UniqueConstraint(
            "giorno_settimana", "tipo_pasto", "opzione", name="uq_piano_slot"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    giorno_settimana: Mapped[int]  # 0 = lunedì ... 6 = domenica
    tipo_pasto: Mapped[str]  # colazione, pranzo, cena, spuntino
    ricetta_id: Mapped[int] = mapped_column(
        ForeignKey("ricette.id", ondelete="CASCADE")
    )
    opzione: Mapped[int] = mapped_column(default=1)

    ricetta: Mapped["Ricetta"] = relationship()


class DiarioVoce(Base):
    __tablename__ = "diario"
    __table_args__ = (CheckConstraint("grammi > 0", name="ck_diario_grammi"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[date]
    tipo_pasto: Mapped[str]
    alimento_id: Mapped[int] = mapped_column(
        ForeignKey("alimenti.id", ondelete="RESTRICT")
    )
    grammi: Mapped[float]

    alimento: Mapped["Alimento"] = relationship()


class Promemoria(Base):
    __tablename__ = "promemoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    titolo: Mapped[str]
    orario: Mapped[time]
    giorni: Mapped[str]  # es. "0,1,2,3,4" (giorni della settimana)
    attivo: Mapped[bool] = mapped_column(default=True)
