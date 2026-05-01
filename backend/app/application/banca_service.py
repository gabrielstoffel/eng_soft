from app.application import document_service, email_service, petition_service
from app.config import COORDENADOR_EMAIL, FRONTEND_BASE_URL, SECRETARY_EMAIL
from app.domain.banca_repository import BancaRepository
from app.domain.errors import (
    BancaAlreadyDecidedError,
    BancaNotFoundError,
    DocumentGenerationError,
    EmailError,
    PersistenceError,
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

    def submit_petition(self, req: BancaRequest) -> Result[BancaSubmitResponse, EmailError | PersistenceError]:
        logger.info("submit_petition.start", {"ata": req.ata, "student": req.nome.name})

        match self._repo.save(req):
            case Err() as err:
                logger.error("submit_petition.save.error", {"message": err.error.message})
                return err
            case ok:
                token = ok.value

        decision_link = f"{FRONTEND_BASE_URL}/decide/{token}"
        logger.info(
            "submit_petition.send_petition_email.start",
            {"recipient": COORDENADOR_EMAIL, "decision_token": token},
        )
        subject = petition_service.build_petition_subject(req)
        html = petition_service.build_petition_html(req, decision_link)
        match email_service.send_petition_email(COORDENADOR_EMAIL, subject, html):
            case Err() as err:
                logger.error(
                    "submit_petition.send_petition_email.error",
                    {"message": err.error.message, "recipient": COORDENADOR_EMAIL},
                )
                return err
        logger.info(
            "submit_petition.send_petition_email.end",
            {"recipient": COORDENADOR_EMAIL},
        )

        logger.info(
            "submit_petition.end",
            {"ata": req.ata, "decision_token": token, "status": "pending"},
        )
        return Ok(
            BancaSubmitResponse(
                message="Pedido enviado ao coordenador.",
                ata=req.ata,
                student_name=req.nome.name,
                decision_token=token,
            )
        )

    def get_summary(self, token: str) -> Result[BancaSummary, BancaNotFoundError | PersistenceError]:
        logger.info("get_summary.start", {"decision_token": token})
        match self._repo.find_by_token(token):
            case Err() as err:
                return err
            case ok:
                record = ok.value

        summary = BancaSummary(
            request=record.request,
            status=record.status,
            rejection_reason=record.rejection_reason,
        )
        logger.info("get_summary.end", {"decision_token": token, "status": record.status})
        return Ok(summary)

    def approve(
        self, token: str
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
            logger.warn(
                "approve.already_decided",
                {"decision_token": token, "current_status": record.status},
            )
            return Err(
                BancaAlreadyDecidedError(
                    message=f"Banca already decided (status={record.status})",
                    current_status=record.status,
                )
            )

        req = record.request

        logger.info("approve.generate_documents.start", {"ata": req.ata})
        match document_service.generate_documents(req):
            case Err() as err:
                logger.error("approve.generate_documents.error", {"message": err.error.message})
                return err
            case ok:
                zip_bytes, zip_name = ok.value
        logger.info("approve.generate_documents.end", {"zip": zip_name})

        logger.info("approve.send_documents_email.start", {"recipient": SECRETARY_EMAIL})
        docs_subject = f"[SigBah!] Documentos da Banca #{req.ata} — {req.nome.name}"
        docs_html = petition_service.build_documents_html(req)
        match email_service.send_documents_email(SECRETARY_EMAIL, docs_subject, docs_html, zip_bytes, zip_name):
            case Err() as err:
                logger.error(
                    "approve.send_documents_email.error",
                    {"message": err.error.message, "recipient": SECRETARY_EMAIL},
                )
                return err
        logger.info("approve.send_documents_email.end", {"recipient": SECRETARY_EMAIL})

        match self._repo.update_decision(token, "approved"):
            case Err() as err:
                logger.error(
                    "approve.update_decision.error",
                    {"decision_token": token, "message": err.error.message},
                )
                return err

        logger.info(
            "approve.end",
            {"decision_token": token, "ata": req.ata, "status": "approved"},
        )
        return Ok(
            BancaDecisionResponse(
                message="Banca aprovada e documentos enviados à secretaria.",
                ata=req.ata,
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
            logger.warn(
                "reject.already_decided",
                {"decision_token": token, "current_status": record.status},
            )
            return Err(
                BancaAlreadyDecidedError(
                    message=f"Banca already decided (status={record.status})",
                    current_status=record.status,
                )
            )

        req = record.request

        match self._repo.update_decision(token, "rejected", reason=reason):
            case Err() as err:
                logger.error(
                    "reject.update_decision.error",
                    {"decision_token": token, "message": err.error.message},
                )
                return err

        recipient = req.orientador.email
        logger.info(
            "reject.send_rejection_email.start",
            {"recipient": recipient, "decision_token": token},
        )
        subject = petition_service.build_rejection_subject(req)
        html = petition_service.build_rejection_html(req, reason)
        match email_service.send_rejection_email(recipient, subject, html):
            case Err() as err:
                logger.error(
                    "reject.send_rejection_email.error",
                    {"message": err.error.message, "recipient": recipient},
                )
                return err
        logger.info(
            "reject.send_rejection_email.end",
            {"recipient": recipient},
        )

        logger.info(
            "reject.end",
            {"decision_token": token, "ata": req.ata, "status": "rejected"},
        )
        return Ok(
            BancaDecisionResponse(
                message="Banca rejeitada e submetente notificado.",
                ata=req.ata,
                student_name=req.nome.name,
            )
        )
