from pydantic import BaseModel, ConfigDict, Field, computed_field


class AlimentoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    kcal: float = Field(ge=0)
    proteine: float = Field(ge=0)
    carboidrati: float = Field(ge=0)
    grassi: float = Field(ge=0)


class AlimentoCreate(AlimentoBase):
    pass


class AlimentoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    kcal: float | None = Field(default=None, ge=0)
    proteine: float | None = Field(default=None, ge=0)
    carboidrati: float | None = Field(default=None, ge=0)
    grassi: float | None = Field(default=None, ge=0)


class AlimentoOut(AlimentoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class IngredienteIn(BaseModel):
    alimento_id: int
    grammi: float = Field(gt=0)


class IngredienteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    alimento: AlimentoOut
    grammi: float


class RicettaCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    istruzioni: str | None = None
    ingredienti: list[IngredienteIn] = Field(min_length=1)


class RicettaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    istruzioni: str | None = None
    # se presente, sostituisce tutti gli ingredienti esistenti
    ingredienti: list[IngredienteIn] | None = Field(default=None, min_length=1)


class MacroTotali(BaseModel):
    kcal: float
    proteine: float
    carboidrati: float
    grassi: float


class RicettaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    istruzioni: str | None
    ingredienti: list[IngredienteOut]

    @computed_field
    @property
    def macro(self) -> MacroTotali:
        tot = {"kcal": 0.0, "proteine": 0.0, "carboidrati": 0.0, "grassi": 0.0}
        for ing in self.ingredienti:
            fattore = ing.grammi / 100
            for campo in tot:
                tot[campo] += getattr(ing.alimento, campo) * fattore
        return MacroTotali(**{k: round(v, 1) for k, v in tot.items()})
