from datetime import date, time
from typing import Literal

from pydantic import BaseModel


class MemberInfo(BaseModel):
    gender: Literal[0, 1]  # 0=Prof. Dr., 1=Profª. Drª.
    name: str
    institution: str
    location: str  # e.g. "Porto Alegre, RS"
    lang: Literal["pt", "en"]

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
    externo1: MemberInfo
    externo2: MemberInfo | None = None
    interno1: MemberInfo
    interno2: MemberInfo
    supl_int: MemberInfo | None = None
    supl_ext: MemberInfo | None = None
    titulo: str
    titulo2: str


class BancaResponse(BaseModel):
    message: str
    ata: int
    student_name: str
    zip_name: str
