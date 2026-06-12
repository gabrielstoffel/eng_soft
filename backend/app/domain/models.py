from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


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
    # ppgenfis: data de envio do parecer individual mostrada nas cartas-convite.
    # Opcional; quando ausente o gerador usa a data da defesa como fallback.
    data_parecer: date | None = None
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

    # NOTE: business rules (antecedência, composição por tipo, campos obrigatórios
    # por PPG, orientador.email) live in app.application.banca_validation — NOT as
    # model validators. Keeping them off the model ensures records reconstructed
    # from MongoDB are never re-validated against today's date and stay readable
    # over time.


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


class InviteStatus(BaseModel):
    """Send status for a single carta-convite or parecer (keyed by manifest id)."""
    sent: bool = False
    sent_at: datetime | None = None
    recipient: str | None = None


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
    invite_status: dict[str, InviteStatus] = Field(default_factory=dict)

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
    ata: int
    ppg: str
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


# --- Envio de convites/pareceres (Secretaria) ---

InviteKind = Literal["carta_convite", "parecer"]


class InviteItem(BaseModel):
    """A sendable document (carta-convite or parecer) for one banca member."""
    item_id: str                       # manifest id, e.g. "carta_convite:externo1"
    kind: InviteKind
    label: str
    member_role: MemberRole | None = None
    member_name: str | None = None
    recipient: str | None = None       # member email (None => cannot be sent)
    sent: bool = False
    sent_at: datetime | None = None


class SendInvitesRequest(BaseModel):
    item_ids: list[str] = Field(min_length=1)


class InviteSendResult(BaseModel):
    item_id: str
    ok: bool
    error: str | None = None
    sent_at: datetime | None = None
    recipient: str | None = None


class SendInvitesResponse(BaseModel):
    results: list[InviteSendResult]


# --- Admin auth ---

class AdminUserRecord(BaseModel):
    """Stored admin user, including the password hash (never sent to clients)."""
    username: str
    ppg: str
    password_hash: str


class CurrentUser(BaseModel):
    """The authenticated admin extracted from a bearer token."""
    username: str
    ppg: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    ppg: str
