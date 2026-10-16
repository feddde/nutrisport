from pydantic import BaseModel, ConfigDict, Field


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
