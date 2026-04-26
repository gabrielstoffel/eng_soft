from fastapi import APIRouter, HTTPException

from app.config import COORDENADOR_EMAIL, SECRETARY_EMAIL
from app.models import BancaRequest, BancaResponse
from app.result import Err
from app.services import document_service, email_service, petition_service

router = APIRouter()


@router.post("/banca")
def create_banca(req: BancaRequest) -> BancaResponse:
    match document_service.generate_documents(req):
        case Err(error):
            raise HTTPException(status_code=500, detail=f"Document generation failed: {error}")
        case ok:
            zip_bytes, zip_name = ok.value

    petition_html = petition_service.build_petition_html(req)
    petition_subject = petition_service.build_petition_subject(req)
    match email_service.send_petition_email(COORDENADOR_EMAIL, petition_subject, petition_html):
        case Err(error):
            raise HTTPException(status_code=500, detail=f"Petition email failed: {error}")

    docs_subject = f"[SigBah!] Documentos da Banca #{req.ata} — {req.nome.name}"
    docs_html = f"""\
<html>
  <body>
    <h2>Documentos da Banca — SigBah!</h2>
    <p>Os documentos foram gerados e estão em anexo (arquivo zip).</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td>{req.nome.name}</td></tr>
      <tr><td><b>Tipo</b></td><td>{petition_service.tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Data</b></td><td>{req.data.strftime("%d/%m/%Y")} às {req.horario.strftime("%H:%M")}</td></tr>
      <tr><td><b>Orientador</b></td><td>{req.orientador.name}</td></tr>
    </table>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""
    match email_service.send_documents_email(SECRETARY_EMAIL, docs_subject, docs_html, zip_bytes, zip_name):
        case Err(error):
            raise HTTPException(status_code=500, detail=f"Documents email failed: {error}")

    return BancaResponse(
        message="Banca created and emails sent successfully.",
        ata=req.ata,
        student_name=req.nome.name,
        zip_name=zip_name,
    )
