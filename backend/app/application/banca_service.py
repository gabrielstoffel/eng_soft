from app.application import document_service, email_service, petition_service
from app.config import COORDENADOR_EMAIL, SECRETARY_EMAIL
from app.domain.banca_repository import BancaRepository
from app.domain.errors import DocumentGenerationError, EmailError, PersistenceError
from app.domain.models import BancaRequest, BancaResponse
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


class BancaService:
    def __init__(self, repo: BancaRepository) -> None:
        self._repo = repo

    def create(self, req: BancaRequest) -> Result[BancaResponse, DocumentGenerationError | EmailError | PersistenceError]:
        logger.info("create.start", {"ata": req.ata, "student": req.nome.name})

        logger.info("create.generate_documents.start", {"ata": req.ata})
        match document_service.generate_documents(req):
            case Err() as err:
                logger.error("create.generate_documents.error", {"message": err.error.message})
                return err
            case ok:
                zip_bytes, zip_name = ok.value
                logger.info("create.generate_documents.end", {"zip": zip_name})

        logger.info("create.send_petition_email.start", {"recipient": COORDENADOR_EMAIL})
        petition_subject = petition_service.build_petition_subject(req)
        petition_html = petition_service.build_petition_html(req)
        match email_service.send_petition_email(COORDENADOR_EMAIL, petition_subject, petition_html):
            case Err() as err:
                logger.error("create.send_petition_email.error", {"message": err.error.message, "recipient": COORDENADOR_EMAIL})
                return err
        logger.info("create.send_petition_email.end", {"recipient": COORDENADOR_EMAIL})

        logger.info("create.send_documents_email.start", {"recipient": SECRETARY_EMAIL})
        docs_subject = f"[SigBah!] Documentos da Banca #{req.ata} — {req.nome.name}"
        docs_html = petition_service.build_documents_html(req)
        match email_service.send_documents_email(SECRETARY_EMAIL, docs_subject, docs_html, zip_bytes, zip_name):
            case Err() as err:
                logger.error("create.send_documents_email.error", {"message": err.error.message, "recipient": SECRETARY_EMAIL})
                return err
        logger.info("create.send_documents_email.end", {"recipient": SECRETARY_EMAIL})

        logger.info("create.save.start", {"ata": req.ata})
        match self._repo.save(req):
            case Err() as err:
                logger.error("create.save.error", {"message": err.error.message})
                return err
        logger.info("create.save.end", {"ata": req.ata})

        logger.info("create.end", {"ata": req.ata, "zip": zip_name})
        return Ok(BancaResponse(
            message="Banca created and emails sent successfully.",
            ata=req.ata,
            student_name=req.nome.name,
            zip_name=zip_name,
        ))
