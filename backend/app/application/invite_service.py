"""Sending of cartas-convite and pareceres to banca members (Secretaria).

Implements plan §2.7 / Fase 6 (S1–S5): per-member send, batch send, and a
per-item sent/not-sent/date status. Item identity reuses the document manifest
ids produced by `document_service` (e.g. "carta_convite:externo1",
"parecer:interno1"), so status keys line up 1:1 with generated PDFs.
"""

import io
import zipfile
from datetime import datetime, timezone

from app.application import attachment_service, document_service, email_service, petition_service
from app.config.ppg_profiles import get_profile
from app.domain.banca_repository import BancaRepository
from app.domain.errors import (
    BancaNotEditableError,
    BancaNotFoundError,
    PersistenceError,
)
from app.domain.models import (
    BancaRecord,
    InviteItem,
    InviteSendResult,
    InviteStatus,
    SendInvitesResponse,
)
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)

_INVITE_KINDS = ("carta_convite", "parecer")

# Above this size the thesis/dissertation PDF is zipped before being attached.
_MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024


def _zip_one(filename: str, content: bytes) -> tuple[str, bytes, str]:
    """Zip a single file; returns (zip_name, zip_bytes, mime)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, content)
    buf.seek(0)
    zip_name = filename.rsplit(".", 1)[0] + ".zip"
    return zip_name, buf.read(), "application/zip"


def _prepare_thesis_attachments(token: str) -> list[tuple[str, bytes, str]]:
    """Load the uploaded thesis/dissertation/exam PDF(s), zipping any that are large."""
    prepared: list[tuple[str, bytes, str]] = []
    for filename, content, content_type in attachment_service.load_attachments(token, kind="texto"):
        if len(content) > _MAX_ATTACHMENT_BYTES:
            name, data, mime = _zip_one(filename, content)
            prepared.append((name, data, mime))
        else:
            prepared.append((filename, content, content_type))
    return prepared


class InviteService:
    def __init__(self, repo: BancaRepository) -> None:
        self._repo = repo

    def _build_items(self, record: BancaRecord) -> list[InviteItem]:
        req = record.request
        items: list[InviteItem] = []
        for entry in document_service.file_manifest(req):
            if entry.kind not in _INVITE_KINDS:
                continue
            member = getattr(req, entry.member_role, None) if entry.member_role else None
            status = record.invite_status.get(entry.id, InviteStatus())
            # For an already-sent item show the address it was actually sent to
            # (persisted at send time); otherwise the member's current email.
            recipient = status.recipient if status.sent else (member.email if member else None)
            items.append(
                InviteItem(
                    item_id=entry.id,
                    kind=entry.kind,
                    label=entry.label,
                    member_role=entry.member_role,
                    member_name=member.name if member else None,
                    recipient=recipient,
                    sent=status.sent,
                    sent_at=status.sent_at,
                )
            )
        return items

    def list_invites(
        self, token: str
    ) -> Result[list[InviteItem], BancaNotFoundError | PersistenceError]:
        logger.info("invite.list.start", {"decision_token": token})
        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value
        return Ok(self._build_items(record))

    def send_invites(
        self, token: str, item_ids: list[str]
    ) -> Result[
        SendInvitesResponse,
        BancaNotFoundError | BancaNotEditableError | PersistenceError,
    ]:
        logger.info("invite.send.start", {"decision_token": token, "item_ids": item_ids})
        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value

        # Convites/pareceres só fazem sentido após a aprovação da banca.
        if record.status != "approved":
            return Err(
                BancaNotEditableError(
                    message=f"Banca precisa estar aprovada para enviar convites (status={record.status})",
                    current_status=record.status,
                )
            )

        items_by_id = {item.item_id: item for item in self._build_items(record)}
        req = record.request
        profile = get_profile(record.ppg)

        # The thesis/dissertation/exam PDF travels with every invite.
        thesis_attachments = _prepare_thesis_attachments(token)

        results: list[InviteSendResult] = []
        for item_id in item_ids:
            item = items_by_id.get(item_id)
            if item is None:
                results.append(InviteSendResult(item_id=item_id, ok=False, error="Item desconhecido"))
                continue
            if not item.recipient:
                results.append(
                    InviteSendResult(item_id=item_id, ok=False, error="Membro sem e-mail cadastrado")
                )
                continue

            member = getattr(req, item.member_role)

            # Generate the single PDF for this item.
            match document_service.generate_files(req, [item_id], record.ata):
                case Err() as err:
                    logger.error("invite.send.document_error", {"item_id": item_id, "message": err.error.message})
                    results.append(InviteSendResult(item_id=item_id, ok=False, error=err.error.message))
                    continue
                case ok:
                    buf, filename, mime = ok.value

            subject = petition_service.build_invite_subject(req, item.kind)
            html = petition_service.build_invite_html(req, item.kind, member)
            attachments = [(filename, buf.read(), mime), *thesis_attachments]
            match email_service.send_email_with_attachments(
                item.recipient, subject, html, attachments, cc=profile.secretary_email
            ):
                case Err() as err:
                    logger.error("invite.send.email_error", {"item_id": item_id, "message": err.error.message})
                    results.append(InviteSendResult(item_id=item_id, ok=False, error=err.error.message))
                    continue

            now = datetime.now(timezone.utc)
            status = InviteStatus(sent=True, sent_at=now, recipient=item.recipient)
            match self._repo.set_invite_status(token, item_id, status):
                case Err() as err:
                    logger.error("invite.send.persist_error", {"item_id": item_id, "message": err.error.message})
                    results.append(InviteSendResult(item_id=item_id, ok=False, error=err.error.message))
                    continue

            results.append(
                InviteSendResult(item_id=item_id, ok=True, sent_at=now, recipient=item.recipient)
            )

        logger.info(
            "invite.send.end",
            {"decision_token": token, "sent": sum(1 for r in results if r.ok), "total": len(results)},
        )
        return Ok(SendInvitesResponse(results=results))
