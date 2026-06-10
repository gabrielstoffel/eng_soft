from app.application import banca_validation, document_service, email_service, petition_service
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
        self, req: BancaRequest
    ) -> Result[BancaSubmitResponse, ValidationError | EmailError | PersistenceError]:
        logger.info("submit_petition.start", {"student": req.nome.name, "ppg": req.ppg})
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

        decision_link = f"{FRONTEND_BASE_URL}/decide/{token}"
        subject = petition_service.build_petition_subject(req, record.ata)
        html = petition_service.build_petition_html(req, decision_link)
        match email_service.send_email(profile.coordenador_email, subject, html):
            case Err() as err:
                return err

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

        # Generate documents FIRST. Generation is pure and has no side effects,
        # so a failure here leaves the banca "pending" and the approval can be
        # safely retried (instead of getting stuck "approved" but undelivered).
        match document_service.generate_documents(req, record.ata):
            case Err() as err:
                logger.error(
                    "approve.document_generation.error",
                    {"decision_token": token, "message": err.error.message},
                )
                return err
            case ok:
                zip_bytes, zip_name = ok.value

        # Commit the decision via the atomic pending→approved transition, BEFORE
        # sending any email. Under concurrency/retries only the caller that wins
        # this transition reaches the email sends, so the documents/scheduling
        # emails can never be fired twice.
        match self._repo.update_decision(token, "approved", observation=observation):
            case Err() as err:
                return err

        # Send documents to secretary (with observation if present)
        docs_subject = f"[SigBah!] Documentos da Banca #{record.ata} — {req.nome.name}"
        docs_html = petition_service.build_documents_html(req, record.ata, observation)
        match email_service.send_documents_email(profile.secretary_email, docs_subject, docs_html, zip_bytes, zip_name):
            case Err() as err:
                return err

        # Send scheduling email to gerência with CC to CPG alias
        gerencia_subject = f"[SigBah!] Solicitação de Agendamento — Banca #{record.ata}"
        gerencia_html = petition_service.build_gerencia_html(req, record.ata, profile)
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
        subject = petition_service.build_rejection_subject(req, record.ata)
        html = petition_service.build_rejection_html(req, record.ata, reason)
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
