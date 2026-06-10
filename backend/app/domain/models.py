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
    remoto: bool = False
    ppg: str | None = None
    bolsista_cnpq: bool | None = None
    nivel_cnpq: str | None = None
    lattes: str | None = None
    doctorate_institution: str | None = None
    doctorate_year: int | None = None

    def to_tuple(self) -> tuple:
        return (self.gender, self.name, self.institution, self.location, self.lang)


class StudentInfo(BaseModel):
    gender: Literal[0, 1]
    name: str
    cpf: str | None = None
    birth_date: date | None = None
    email: EmailStr | None = None

    def to_tuple(self) -> tuple:
        return (self.gender, self.name)


class BancaRequest(BaseModel):
    ppg: Literal["ppgfis", "ppgenfis"]
    nome: StudentInfo
    tipo: Literal[1, 2, 3]  # 1=Mestrado, 2=Qualificação, 3=Doutorado
    data: date
    horario: time
    modalidade: Literal["presencial", "hibrida", "remota"]
    sala_preferencia: str | None = None
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
    titulo2: str | None = None
    comentario_desempenho: str | None = None
    justificativa_membros: str | None = None

    @model_validator(mode="after")
    def _require_orientador_email(self) -> "BancaRequest":
        if not self.orientador.email:
            raise ValueError("orientador.email is required")
        return self

    @model_validator(mode="after")
    def _validate_modalidade_fields(self) -> "BancaRequest":
        if self.modalidade in ("presencial", "hibrida") and not self.sala_preferencia:
            raise ValueError("sala_preferencia is required for presencial/híbrida")
        return self

    @model_validator(mode="after")
    def _enforce_tipo_rules(self) -> "BancaRequest":
        from app.config.ppg_profiles import get_profile
        profile = get_profile(self.ppg)
        rules = profile.roles_by_tipo[self.tipo]
        for slot, presence in rules.items():
            value = getattr(self, slot, None)
            if presence == "required" and value is None:
                raise ValueError(f"{slot} is required for {self.ppg} tipo {self.tipo}")
            if presence == "hidden" and value is not None:
                raise ValueError(f"{slot} must not be set for {self.ppg} tipo {self.tipo}")
        return self

    @model_validator(mode="after")
    def _validate_antecedencia(self) -> "BancaRequest":
        from app.config.ppg_profiles import get_profile
        profile = get_profile(self.ppg)
        min_days = profile.antecedencia_dias[self.tipo]
        days_ahead = (self.data - date.today()).days
        if days_ahead < min_days:
            raise ValueError(
                f"Data deve ter no mínimo {min_days} dias de antecedência "
                f"para {self.ppg} tipo {self.tipo} (tem {days_ahead})"
            )
        return self

    @model_validator(mode="after")
    def _validate_ppg_specific_fields(self) -> "BancaRequest":
        if self.ppg == "ppgenfis":
            # Student fields required for PPGEnFis
            if not self.nome.cpf:
                raise ValueError("nome.cpf is required for ppgenfis")
            if not self.nome.birth_date:
                raise ValueError("nome.birth_date is required for ppgenfis")
            if not self.nome.email:
                raise ValueError("nome.email is required for ppgenfis")
            # Member fields required for PPGEnFis
            members = [
                ("orientador", self.orientador),
                ("coorientador", self.coorientador),
                ("externo1", self.externo1),
                ("externo2", self.externo2),
                ("interno1", self.interno1),
                ("interno2", self.interno2),
                ("supl_int", self.supl_int),
                ("supl_ext", self.supl_ext),
            ]
            for role, member in members:
                if member is None:
                    continue
                if not member.lattes:
                    raise ValueError(f"{role}.lattes is required for ppgenfis")
                if not member.doctorate_institution:
                    raise ValueError(f"{role}.doctorate_institution is required for ppgenfis")
                if not member.doctorate_year:
                    raise ValueError(f"{role}.doctorate_year is required for ppgenfis")
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
    approval_observation: str | None = None
    ata: int
    ppg: str
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
    approval_observation: str | None = None


class BancaDecisionResponse(BaseModel):
    message: str
    ata: int
    student_name: str


class ApproveRequest(BaseModel):
    observation: str | None = None


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1)


class BancaListFilters(BaseModel):
    status: BancaStatus | None = None
    ata: int | None = None
    student: str | None = None
    orientador: str | None = None
    ppg: str | None = None
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
    ppg: str
    created_at: datetime


class BancaAdminDetail(BaseModel):
    decision_token: str
    status: BancaStatus
    rejection_reason: str | None = None
    approval_observation: str | None = None
    current_version: int
    versions: list[BancaVersion]
    ata: int
    ppg: str
    created_at: datetime
    decided_at: datetime | None = None


class BancaUpdateResponse(BaseModel):
    created_new_version: bool
    current_version: int
