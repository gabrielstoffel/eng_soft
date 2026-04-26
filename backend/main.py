import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "localhost"
SMTP_PORT = 2525

FROM = "sigbah@sigbah.local"
TO = "secretario@ufrgs.br"

msg = MIMEMultipart("alternative")
msg["Subject"] = "Teste SigBah! - Pedido de Banca"
msg["From"] = FROM
msg["To"] = TO

html = """\
<html>
  <body>
    <h2>Novo Pedido de Banca — SigBah!</h2>
    <p>Este é um e-mail de teste do sistema <strong>SigBah!</strong>.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td>João da Silva</td></tr>
      <tr><td><b>Tipo</b></td><td>Dissertação de Mestrado</td></tr>
      <tr><td><b>Data</b></td><td>2026-06-10 14:00</td></tr>
    </table>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""

msg.attach(MIMEText(html, "html"))

with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    server.sendmail(FROM, [TO], msg.as_string())

print(f"E-mail enviado! Acesse http://localhost:8025 para visualizar.")
