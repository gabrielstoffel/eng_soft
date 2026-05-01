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

    @model_validator(mode="after")
    def _enforce_tipo_rules(self) -> "BancaRequest":
        rules: dict[int, dict[str, str]] = {
            1: {  # Mestrado
                "orientador": "required",
                "coorientador": "optional",
                "externo1": "required",
                "externo2": "hidden",
                "interno1": "required",
                "interno2": "required",
                "supl_int": "optional",
                "supl_ext": "optional",
            },
            2: {  # Exame de Qualificação ao Doutorado
                "orientador": "required",
                "coorientador": "optional",
                "externo1": "required",
                "externo2": "optional",
                "interno1": "required",
                "interno2": "required",
                "supl_int": "optional",
                "supl_ext": "optional",
            },
            3: {  # Doutorado
                "orientador": "required",
                "coorientador": "optional",
                "externo1": "required",
                "externo2": "required",
                "interno1": "required",
                "interno2": "required",
                "supl_int": "optional",
                "supl_ext": "optional",
            },
        }
        for slot, presence in rules[self.tipo].items():
            value = getattr(self, slot)
            if presence == "required" and value is None:
                raise ValueError(f"{slot} is required for tipo {self.tipo}")
            if presence == "hidden" and value is not None:
                raise ValueError(f"{slot} must not be set for tipo {self.tipo}")
        return self


BancaStatus = Literal["pending", "approved", "rejected"]

DocumentKind = Literal["ata", "carta_convite", "parecer", "cartaz", "relatoria_avaliacao"]

MemberRole = Literal[
    "orientador",
    "coorientador",
    "externo1",
    "externo2",
    "interno1",
    "interno2",
    "supl_int",
    "supl_ext",
]


class FileManifestEntry(BaseModel):
    id: str
    label: str
    kind: DocumentKind
    member_role: MemberRole | None = None


class BancaVersion(BaseModel):
    version: int
    request: BancaRequest
    created_at: datetime


class BancaRecord(BaseModel):
    versions: list[BancaVersion]
    current_version: int
    decision_token: str
    status: BancaStatus
    rejection_reason: str | None = None
    created_at: datetime
    decided_at: datetime | None = None

    @property
    def request(self) -> BancaRequest:
        for v in self.versions:
            if v.version == self.current_version:
                return v.request
        return self.versions[-1].request


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


class BancaListFilters(BaseModel):
    status: BancaStatus | None = None
    ata: int | None = None
    student: str | None = None
    orientador: str | None = None
    q: str | None = None


class BancaListItem(BaseModel):
    decision_token: str
    ata: int
    student_name: str
    status: BancaStatus
    current_version: int
    tipo: Literal[1, 2, 3]
    data: date
    orientador_name: str
    created_at: datetime


class BancaAdminDetail(BaseModel):
    decision_token: str
    status: BancaStatus
    rejection_reason: str | None = None
    current_version: int
    versions: list[BancaVersion]
    created_at: datetime
    decided_at: datetime | None = None


class BancaUpdateResponse(BaseModel):
    created_new_version: bool
    current_version: int
