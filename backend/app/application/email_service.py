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


def send_email(
    to: str, subject: str, html_body: str, cc: str | None = None
) -> Result[None, EmailError]:
    logger.info("send_email.start", {"to": to, "cc": cc})
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDRESS
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg.attach(MIMEText(html_body, "html"))
    recipients = [to] + ([cc] if cc else [])
    return _send(recipients, msg)


def send_documents_email(
    to: str, subject: str, html_body: str, zip_bytes: BytesIO, zip_name: str, cc: str | None = None
) -> Result[None, EmailError]:
    logger.info("send_documents_email.start", {"to": to, "zip": zip_name})
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDRESS
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg.attach(MIMEText(html_body, "html"))

    part = MIMEBase("application", "zip")
    part.set_payload(zip_bytes.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=zip_name)
    msg.attach(part)

    recipients = [to] + ([cc] if cc else [])
    return _send(recipients, msg)


def send_attachment_email(
    to: str,
    subject: str,
    html_body: str,
    attachment: bytes,
    filename: str,
    mime_type: str = "application/pdf",
    cc: str | None = None,
) -> Result[None, EmailError]:
    """Send an HTML email with a single binary attachment (e.g. a single PDF)."""
    logger.info("send_attachment_email.start", {"to": to, "filename": filename})
    maintype, _, subtype = mime_type.partition("/")
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDRESS
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg.attach(MIMEText(html_body, "html"))

    part = MIMEBase(maintype or "application", subtype or "octet-stream")
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(part)

    recipients = [to] + ([cc] if cc else [])
    return _send(recipients, msg)


# Legacy aliases for backward compatibility
def send_petition_email(to: str, subject: str, html_body: str) -> Result[None, EmailError]:
    return send_email(to, subject, html_body)


def send_rejection_email(to: str, subject: str, html_body: str) -> Result[None, EmailError]:
    return send_email(to, subject, html_body)


def _send(recipients: list[str], msg: MIMEMultipart) -> Result[None, EmailError]:
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(msg["From"], recipients, msg.as_string())
        logger.info("_send.end", {"recipients": recipients})
        return Ok(None)
    except Exception as e:
        logger.error("_send.error", {"recipients": recipients, "message": str(e)})
        return Err(EmailError(message=str(e), recipient=recipients[0]))
