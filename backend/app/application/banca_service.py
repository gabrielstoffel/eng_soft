from app.application import attachment_service, banca_validation, email_service, petition_service
from app.application.attachment_service import AttachmentUpload
from app.config import FRONTEND_BASE_URL
from app.config.ppg_profiles import get_profile
from app.domain.banca_repository import BancaRepository
from app.domain.errors import (
    BancaAlreadyDecidedError,
    BancaNotFoundError,
    DocumentGenerationError,
    EmailError,
    PersistenceError,
    ValidationError,
)
from app.domain.models import (
    BancaDecisionResponse,
    BancaRequest,
    BancaSubmitResponse,
    BancaSummary,
)
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class BancaService:
    def __init__(self, repo: BancaRepository) -> None:
        self._repo = repo

    def submit_petition(
        self, req: BancaRequest, attachments: list[AttachmentUpload] | None = None
    ) -> Result[BancaSubmitResponse, ValidationError | EmailError | PersistenceError]:
        attachments = attachments or []
        logger.info(
            "submit_petition.start",
            {"student": req.nome.name, "ppg": req.ppg, "attachments": len(attachments)},
        )
        profile = get_profile(req.ppg)

        errors = banca_validation.validate_submission(req)
        if errors:
            logger.info("submit_petition.validation_failed", {"errors": errors})
            return Err(ValidationError(message="; ".join(errors), details=errors))

        match self._repo.save(req):
            case Err() as err:
                return err
            case ok:
                token = ok.value

        # Get the ata that was assigned
        match self._repo.find_by_token(token):
            case Err() as err:
                return Err(PersistenceError(message="Failed to retrieve saved banca"))
            case ok:
                record = ok.value

        # Persist the uploaded PDFs (system of record) and attach them to the
        # coordenador email so they travel with the petition.
        attachment_service.store_attachments(token, attachments)

        decision_link = f"{FRONTEND_BASE_URL}/decide/{token}"
        admin_link = f"{FRONTEND_BASE_URL}/admin"
        subject = petition_service.build_petition_subject(req)
        html = petition_service.build_petition_html(req, decision_link)
        email_files = [(a.filename, a.content, a.content_type) for a in attachments]
        match email_service.send_email_with_attachments(
            profile.coordenador_email, subject, html, email_files
        ):
            case Err() as err:
                return err

        # Also notify the secretary that a new banca arrived for evaluation.
        sec_subject = petition_service.build_secretary_notification_subject(req)
        sec_html = petition_service.build_secretary_notification_html(req, admin_link)
        match email_service.send_email(profile.secretary_email, sec_subject, sec_html):
            case Err() as err:
                logger.error("submit_petition.secretary_email.error", {"message": err.error.message})
                # Non-fatal: the coordenador (the decision-maker) was already notified.

        logger.info("submit_petition.end", {"ata": record.ata, "decision_token": token})
        return Ok(
            BancaSubmitResponse(
                message="Pedido enviado ao coordenador.",
                ata=record.ata,
                student_name=req.nome.name,
                decision_token=token,
            )
        )

    def get_summary(self, token: str) -> Result[BancaSummary, BancaNotFoundError | PersistenceError]:
        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value
        return Ok(
            BancaSummary(
                request=record.request,
                ata=record.ata,
                ppg=record.ppg,
                status=record.status,
                rejection_reason=record.rejection_reason,
                approval_observation=record.approval_observation,
            )
        )

    def approve(
        self, token: str, observation: str | None = None
    ) -> Result[
        BancaDecisionResponse,
        BancaNotFoundError | BancaAlreadyDecidedError | DocumentGenerationError | EmailError | PersistenceError,
    ]:
        logger.info("approve.start", {"decision_token": token})

        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value

        if record.status != "pending":
            return Err(
                BancaAlreadyDecidedError(
                    message=f"Banca already decided (status={record.status})",
                    current_status=record.status,
                )
            )

        req = record.request
        profile = get_profile(record.ppg)

        # Commit the decision via the atomic pending→approved transition, BEFORE
        # sending any email. Under concurrency/retries only the caller that wins
        # this transition reaches the email sends, so the notification/scheduling
        # emails can never be fired twice.
        match self._repo.update_decision(token, "approved", observation=observation):
            case Err() as err:
                return err

        # Notify the secretary (no attachments — documents are downloaded from the
        # admin panel; cartas-convite/pareceres are sent separately from there).
        docs_subject = f"[SigBah!] Documentos — {petition_service.tipo_label(req.tipo)} — {req.nome.name}"
        admin_link = f"{FRONTEND_BASE_URL}/admin"
        docs_html = petition_service.build_documents_html(req, admin_link, observation)
        match email_service.send_email(profile.secretary_email, docs_subject, docs_html):
            case Err() as err:
                return err

        # Notify the orientador that the banca was approved.
        if req.orientador.email:
            orient_subject = petition_service.build_orientador_approval_subject(req)
            orient_html = petition_service.build_orientador_approval_html(req, observation)
            match email_service.send_email(req.orientador.email, orient_subject, orient_html):
                case Err() as err:
                    logger.error("approve.orientador_email.error", {"message": err.error.message})
                    # Non-fatal: the banca is already approved.

        # Send scheduling email to gerência with CC to CPG alias
        gerencia_subject = f"[SigBah!] Solicitação de Agendamento — {petition_service.tipo_label(req.tipo)} — {req.nome.name}"
        gerencia_html = petition_service.build_gerencia_html(req, profile)
        match email_service.send_email(profile.gerencia_email, gerencia_subject, gerencia_html, cc=profile.cpg_alias_email):
            case Err() as err:
                logger.error("approve.gerencia_email.error", {"message": err.error.message})
                # Non-fatal: the banca is already approved; gerência can be re-notified.

        logger.info("approve.end", {"decision_token": token, "ata": record.ata})
        return Ok(
            BancaDecisionResponse(
                message="Banca aprovada e documentos enviados à secretaria.",
                ata=record.ata,
                student_name=req.nome.name,
            )
        )

    def reject(
        self, token: str, reason: str
    ) -> Result[
        BancaDecisionResponse,
        BancaNotFoundError | BancaAlreadyDecidedError | EmailError | PersistenceError,
    ]:
        logger.info("reject.start", {"decision_token": token})

        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value

        if record.status != "pending":
            return Err(
                BancaAlreadyDecidedError(
                    message=f"Banca already decided (status={record.status})",
                    current_status=record.status,
                )
            )

        req = record.request

        match self._repo.update_decision(token, "rejected", reason=reason):
            case Err() as err:
                return err

        recipient = req.orientador.email
        subject = petition_service.build_rejection_subject(req)
        html = petition_service.build_rejection_html(req, reason)
        match email_service.send_email(recipient, subject, html):
            case Err() as err:
                return err

        logger.info("reject.end", {"decision_token": token, "ata": record.ata})
        return Ok(
            BancaDecisionResponse(
                message="Banca rejeitada e submetente notificado.",
                ata=record.ata,
                student_name=req.nome.name,
            )
        )
