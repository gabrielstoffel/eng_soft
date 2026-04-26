import io
import os
import smtplib
import sys
import zipfile
from datetime import date, time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "localhost"
SMTP_PORT = 2525
FROM = "sigbah@sigbah.local"
TO = "secretario@ufrgs.br"

# criaBancas uses paths relative to its own directory (Fonts/, images, Bancas/ output)
CRIABANCAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "criaBancas")
os.chdir(CRIABANCAS_DIR)
sys.path.insert(0, CRIABANCAS_DIR)

from criaBancas import Banca  # noqa: E402


# --- Sample banca ---
banca = Banca(
    nome=(0, "João Paulo da Silva"),
    tipo=1,  # 1=Mestrado, 2=Qualificação ao Doutorado, 3=Doutorado
    data=date(2026, 6, 10),
    horario=time(14, 0),
    data_convite=date(2026, 5, 10),
    ata=42,
    local_banca="Sala 215, Prédio 43413 — Campus do Vale",
    link="https://meet.google.com/abc-defg-hij",
    orientador=(0, "Carlos Alberto Souza", "UFRGS", "Porto Alegre, RS", "pt"),
    coorientador=None,
    externo1=(1, "Maria Fernanda Lima", "USP", "São Paulo, SP", "pt"),
    externo2=None,
    interno1=(0, "Roberto Henrique Nunes", "UFRGS", "Porto Alegre, RS", "pt"),
    interno2=(1, "Ana Paula Ferreira", "UFRGS", "Porto Alegre, RS", "pt"),
    supl_int=(0, "Paulo César Martins", "UFRGS", "Porto Alegre, RS", "pt"),
    supl_ext=None,
    titulo="Estudo de Propriedades Ópticas de Nanoestruturas de Carbono",
    titulo2="Study of Optical Properties of Carbon Nanostructures",
)

# --- Generate all documents ---
banca.criaAta(save=True)
banca.criaCartaConvite(save=True)
banca.criaParecer(save=True)
banca.criaCartaz(save=True)

# --- Zip the output folder ---
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(banca.dir):
        for fname in files:
            full_path = os.path.join(root, fname)
            zf.write(full_path, arcname=os.path.relpath(full_path, banca.dir))

zip_buffer.seek(0)
zip_name = f"banca_{banca.ata}_{banca.nome[1].replace(' ', '_')}.zip"

# --- Build email ---
msg = MIMEMultipart("mixed")
msg["Subject"] = f"[SigBah!] Documentos da Banca #{banca.ata} — {banca.nome[1]}"
msg["From"] = FROM
msg["To"] = TO

html = f"""\
<html>
  <body>
    <h2>Documentos da Banca — SigBah!</h2>
    <p>Os documentos foram gerados e estão em anexo (arquivo zip).</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td>{banca.nome[1]}</td></tr>
      <tr><td><b>Tipo</b></td><td>{banca.tipoAta(banca.tipo)}</td></tr>
      <tr><td><b>Data</b></td><td>{banca.data.strftime('%d/%m/%Y')} às {banca.horario.strftime('%H:%M')}</td></tr>
      <tr><td><b>Local</b></td><td>{banca.local_banca}</td></tr>
      <tr><td><b>Orientador</b></td><td>{banca.orientador[1]}</td></tr>
    </table>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""
msg.attach(MIMEText(html, "html"))

attachment = MIMEBase("application", "zip")
attachment.set_payload(zip_buffer.read())
encoders.encode_base64(attachment)
attachment.add_header("Content-Disposition", "attachment", filename=zip_name)
msg.attach(attachment)

# --- Send ---
with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    server.sendmail(FROM, [TO], msg.as_string())

print(
    f"E-mail com '{zip_name}' enviado! Acesse http://localhost:8025 para visualizar.")
