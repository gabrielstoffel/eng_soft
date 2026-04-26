import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

from app.config import FROM_ADDRESS, SMTP_HOST, SMTP_PORT
from app.domain.errors import EmailError
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)


def send_petition_email(to: str, subject: str, html_body: str) -> Result[None, EmailError]:
    logger.info("send_petition_email.start", {"to": to})
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDRESS
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))
    match result := _send(to, msg):
        case Err(error):
            logger.error("send_petition_email.error", {"to": to, "message": error.message})
        case _:
            logger.info("send_petition_email.end", {"to": to})
    return result


def send_documents_email(to: str, subject: str, html_body: str, zip_bytes: BytesIO, zip_name: str) -> Result[None, EmailError]:
    logger.info("send_documents_email.start", {"to": to, "zip": zip_name})
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDRESS
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    part = MIMEBase("application", "zip")
    part.set_payload(zip_bytes.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=zip_name)
    msg.attach(part)

    match result := _send(to, msg):
        case Err(error):
            logger.error("send_documents_email.error", {"to": to, "message": error.message})
        case _:
            logger.info("send_documents_email.end", {"to": to})
    return result


def _send(to: str, msg: MIMEMultipart) -> Result[None, EmailError]:
    logger.info("_send.start", {"to": to, "host": SMTP_HOST, "port": SMTP_PORT})
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(msg["From"], [to], msg.as_string())
        logger.info("_send.end", {"to": to})
        return Ok(None)
    except Exception as e:
        logger.error("_send.error", {"to": to, "message": str(e)})
        return Err(EmailError(message=str(e), recipient=to))
