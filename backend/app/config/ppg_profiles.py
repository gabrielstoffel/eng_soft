import os
from dataclasses import dataclass, field

RoleMode = str  # "required" | "optional" | "hidden"


@dataclass
class PpgProfile:
    ppg_id: str
    name: str
    coordenador_email: str
    secretary_email: str
    cpg_alias_email: str
    gerencia_email: str
    roles_by_tipo: dict[int, dict[str, RoleMode]]
    antecedencia_dias: dict[int, int]
    # Ata base per tipo — the first banca created gets this value + 1 (so 0 → 1).
    ata_start: dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0})
    required_student_fields: list[str] = field(default_factory=list)
    required_member_fields: list[str] = field(default_factory=list)
    titulo_en_required: bool = False
    default_video_link: str | None = None


ROLES_BY_TIPO_PPGFIS: dict[int, dict[str, RoleMode]] = {
    1: {
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "hidden",
        "interno1": "required",
        "interno2": "required",
        "supl_int": "required",
        "supl_ext": "optional",
    },
    2: {
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "optional",
        "interno1": "required",
        "interno2": "required",
        "supl_int": "required",
        "supl_ext": "optional",
    },
    3: {
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "required",
        "interno1": "required",
        "interno2": "required",
        "supl_int": "required",
        "supl_ext": "optional",
    },
}

ROLES_BY_TIPO_PPGENFIS: dict[int, dict[str, RoleMode]] = {
    1: {
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "optional",
        "interno1": "required",
        "interno2": "optional",
        "supl_int": "optional",
        "supl_ext": "optional",
    },
    2: {
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "optional",
        "interno1": "required",
        "interno2": "optional",
        "supl_int": "optional",
        "supl_ext": "optional",
    },
    3: {
        "orientador": "required",
        "coorientador": "optional",
        "externo1": "required",
        "externo2": "required",
        "interno1": "required",
        "interno2": "optional",
        "supl_int": "optional",
        "supl_ext": "optional",
    },
}

PPGFIS = PpgProfile(
    ppg_id="ppgfis",
    name="PPGFís",
    coordenador_email=os.getenv("PPGFIS_COORDENADOR_EMAIL", "coordenador.fis@if.ufrgs.br"),
    secretary_email=os.getenv("PPGFIS_SECRETARY_EMAIL", "secretario.fis@if.ufrgs.br"),
    cpg_alias_email=os.getenv("PPGFIS_CPG_ALIAS_EMAIL", "cpgfis@if.ufrgs.br"),
    gerencia_email=os.getenv("PPGFIS_GERENCIA_EMAIL", "gerencia@if.ufrgs.br"),
    roles_by_tipo=ROLES_BY_TIPO_PPGFIS,
    antecedencia_dias={1: 20, 2: 30, 3: 30},
    ata_start={
        1: int(os.getenv("PPGFIS_ATA_START_MESTRADO", "0")),
        2: int(os.getenv("PPGFIS_ATA_START_QUALIFICACAO", "0")),
        3: int(os.getenv("PPGFIS_ATA_START_DOUTORADO", "0")),
    },
    required_student_fields=[],
    required_member_fields=[],
    titulo_en_required=False,
    default_video_link=None,
)

PPGENFIS = PpgProfile(
    ppg_id="ppgenfis",
    name="PPGEnFis",
    coordenador_email=os.getenv("PPGENFIS_COORDENADOR_EMAIL", "coordenador.enfis@if.ufrgs.br"),
    secretary_email=os.getenv("PPGENFIS_SECRETARY_EMAIL", "secretario.enfis@if.ufrgs.br"),
    cpg_alias_email=os.getenv("PPGENFIS_CPG_ALIAS_EMAIL", "ppgenfis@if.ufrgs.br"),
    gerencia_email=os.getenv("PPGENFIS_GERENCIA_EMAIL", "gerencia@if.ufrgs.br"),
    roles_by_tipo=ROLES_BY_TIPO_PPGENFIS,
    antecedencia_dias={1: 20, 2: 30, 3: 40},
    ata_start={
        1: int(os.getenv("PPGENFIS_ATA_START_MESTRADO", "0")),
        2: int(os.getenv("PPGENFIS_ATA_START_QUALIFICACAO", "0")),
        3: int(os.getenv("PPGENFIS_ATA_START_DOUTORADO", "0")),
    },
    required_student_fields=["cpf", "birth_date", "email"],
    required_member_fields=["lattes", "doctorate_institution", "doctorate_year"],
    titulo_en_required=False,
    default_video_link=None,
)

_PROFILES: dict[str, PpgProfile] = {
    "ppgfis": PPGFIS,
    "ppgenfis": PPGENFIS,
}


def get_profile(ppg_id: str) -> PpgProfile:
    return _PROFILES[ppg_id]
