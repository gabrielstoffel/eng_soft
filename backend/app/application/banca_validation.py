"""Submission-time business validation for bancas.

These rules used to live as `@model_validator` hooks on `BancaRequest`, which
caused them to re-fire every time a record was reconstructed from MongoDB —
making stored bancas unreadable once their suggested date passed. They now live
in the application layer and are invoked explicitly on submit/edit, keeping the
domain model purely structural.
"""

from datetime import date

from app.config.ppg_profiles import get_profile
from app.domain.models import BancaRequest

_MEMBER_SLOTS = [
    "orientador",
    "coorientador",
    "externo1",
    "externo2",
    "interno1",
    "interno2",
    "supl_int",
    "supl_ext",
]


def _structural_errors(req: BancaRequest) -> list[str]:
    """Rules that must always hold, regardless of when they are checked."""
    errors: list[str] = []
    profile = get_profile(req.ppg)

    if not req.orientador.email:
        errors.append("orientador.email é obrigatório")

    if req.modalidade in ("presencial", "hibrida") and not req.sala_preferencia:
        errors.append("sala_preferencia é obrigatório para modalidade presencial/híbrida")

    if profile.titulo_en_required and not req.titulo2:
        errors.append("titulo2 (título em inglês) é obrigatório")

    rules = profile.roles_by_tipo[req.tipo]
    for slot, presence in rules.items():
        value = getattr(req, slot, None)
        if presence == "required" and value is None:
            errors.append(f"{slot} é obrigatório para {req.ppg} tipo {req.tipo}")
        if presence == "hidden" and value is not None:
            errors.append(f"{slot} não deve ser preenchido para {req.ppg} tipo {req.tipo}")

    for field in profile.required_student_fields:
        if not getattr(req.nome, field, None):
            errors.append(f"nome.{field} é obrigatório para {req.ppg}")

    for slot in _MEMBER_SLOTS:
        member = getattr(req, slot, None)
        if member is None:
            continue
        for field in profile.required_member_fields:
            if not getattr(member, field, None):
                errors.append(f"{slot}.{field} é obrigatório para {req.ppg}")

    return errors


def _antecedencia_errors(req: BancaRequest, *, today: date | None = None) -> list[str]:
    """Minimum-notice rule — only meaningful at submission time."""
    profile = get_profile(req.ppg)
    min_days = profile.antecedencia_dias[req.tipo]
    reference = today or date.today()
    days_ahead = (req.data - reference).days
    if days_ahead < min_days:
        return [
            f"Data deve ter no mínimo {min_days} dias de antecedência "
            f"para {req.ppg} tipo {req.tipo} (tem {days_ahead})"
        ]
    return []


def validate_submission(req: BancaRequest, *, today: date | None = None) -> list[str]:
    """Full validation for a brand-new submission."""
    return _structural_errors(req) + _antecedencia_errors(req, today=today)


def validate_edit(req: BancaRequest) -> list[str]:
    """Validation for an admin edit of an existing banca.

    Antecedência is intentionally skipped: editing a banca whose suggested date
    has already passed is legitimate and must not be blocked.
    """
    return _structural_errors(req)
