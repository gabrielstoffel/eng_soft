from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


class MemberInfo(BaseModel):
    gender: Literal[0, 1]  # 0=Prof. Dr., 1=Profª. Drª.
    name: str
    institution: str
    location: str  # e.g. "Porto Alegre, RS"
    lang: Literal["pt", "en"]
    email: EmailStr | None = None

    def to_tuple(self) -> tuple:
        return (self.gender, self.name, self.institution, self.location, self.lang)


class StudentInfo(BaseModel):
    gender: Literal[0, 1]  # 0=masculine, 1=feminine
    name: str

    def to_tuple(self) -> tuple:
        return (self.gender, self.name)


class BancaRequest(BaseModel):
    nome: StudentInfo
    tipo: Literal[1, 2, 3]  # 1=Mestrado, 2=Qualificação, 3=Doutorado
    data: date
    horario: time
    data_convite: date | None = None
    ata: int
    local_banca: str | None = None
    link: str | None = None
    orientador: MemberInfo
    coorientador: MemberInfo | None = None
    externo1: MemberInfo | None = None
    externo2: MemberInfo | None = None
    interno1: MemberInfo | None = None
    interno2: MemberInfo | None = None
    supl_int: MemberInfo | None = None
    supl_ext: MemberInfo | None = None
    titulo: str
    titulo2: str

    @model_validator(mode="after")
    def _require_orientador_email(self) -> "BancaRequest":
        if not self.orientador.email:
            raise ValueError("orientador.email is required (used for petition decision notifications)")
        return self


BancaStatus = Literal["pending", "approved", "rejected"]


class BancaRecord(BaseModel):
    request: BancaRequest
    decision_token: str
    status: BancaStatus
    rejection_reason: str | None = None
    created_at: datetime
    decided_at: datetime | None = None


class BancaSubmitResponse(BaseModel):
    message: str
    ata: int
    student_name: str
    decision_token: str


class BancaSummary(BaseModel):
    request: BancaRequest
    status: BancaStatus
    rejection_reason: str | None = None


class BancaDecisionResponse(BaseModel):
    message: str
    ata: int
    student_name: str


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1)
