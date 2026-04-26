import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO

from app.config import FROM_ADDRESS, SMTP_HOST, SMTP_PORT
from app.result import Err, Ok, Result


def send_petition_email(to: str, subject: str, html_body: str) -> Result[None, str]:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_ADDRESS
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))
    return _send(to, msg)


def send_documents_email(
    to: str,
    subject: str,
    html_body: str,
    zip_bytes: BytesIO,
    zip_name: str,
) -> Result[None, str]:
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

    return _send(to, msg)


def _send(to: str, msg: MIMEMultipart) -> Result[None, str]:
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(msg["From"], [to], msg.as_string())
        return Ok(None)
    except Exception as e:
        return Err(str(e))
