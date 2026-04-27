from app.domain.models import BancaRequest, MemberInfo

_TIPO_LABEL = {
    1: "Dissertação de Mestrado",
    2: "Exame de Qualificação ao Doutorado",
    3: "Tese de Doutorado",
}


def tipo_label(tipo: int) -> str:
    return _TIPO_LABEL[tipo]


def build_petition_subject(req: BancaRequest) -> str:
    return f"[SigBah!] Novo Pedido de Banca #{req.ata} — {req.nome.name}"


_DECISION_BUTTON_STYLE = (
    "display:inline-block;padding:10px 20px;background:#3b82f6;"
    "color:#fff;text-decoration:none;border-radius:4px;font-weight:600;"
)


def build_petition_html(req: BancaRequest, decision_link: str) -> str:
    membros_rows = ""
    pairs: list[tuple[str, MemberInfo | None]] = [
        ("Orientador", req.orientador),
        ("Coorientador", req.coorientador),
        ("Externo 1", req.externo1),
        ("Externo 2", req.externo2),
        ("Interno 1", req.interno1),
        ("Interno 2", req.interno2),
        ("Suplente Interno", req.supl_int),
        ("Suplente Externo", req.supl_ext),
    ]
    for label, member in pairs:
        if member is None:
            continue
        membros_rows += f"<tr><td><b>{label}</b></td><td>{member.name}</td><td>{member.institution}</td></tr>\n"

    local_parts = []
    if req.local_banca:
        local_parts.append(req.local_banca)
    if req.link:
        local_parts.append(f'<a href="{req.link}">{req.link}</a>')
    local_str = " / ".join(local_parts) if local_parts else "—"
    data_hora = f"{req.data.strftime('%d/%m/%Y')} às {req.horario.strftime('%H:%M')}"

    return f"""\
<html>
  <body>
    <h2>Novo Pedido de Banca — SigBah!</h2>
    <p>Uma nova banca foi submetida e aguarda sua decisão.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td colspan="2">{req.nome.name}</td></tr>
      <tr><td><b>Tipo</b></td><td colspan="2">{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Data</b></td><td colspan="2">{data_hora}</td></tr>
      <tr><td><b>Local / Link</b></td><td colspan="2">{local_str}</td></tr>
      <tr><td><b>Número da Ata</b></td><td colspan="2">{req.ata}</td></tr>
      <tr><td><b>Título (PT)</b></td><td colspan="2">{req.titulo}</td></tr>
      <tr><td><b>Title (EN)</b></td><td colspan="2">{req.titulo2}</td></tr>
    </table>
    <h3>Membros da Banca</h3>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>Função</th><th>Nome</th><th>Instituição</th></tr>
      {membros_rows}
    </table>
    <p style="margin-top: 1.5rem;">
      <a href="{decision_link}" style="{_DECISION_BUTTON_STYLE}">Acessar página de decisão</a>
    </p>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""


def build_documents_html(req: BancaRequest) -> str:
    return f"""\
<html>
  <body>
    <h2>Documentos da Banca — SigBah!</h2>
    <p>Os documentos foram gerados e estão em anexo (arquivo zip).</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td>{req.nome.name}</td></tr>
      <tr><td><b>Tipo</b></td><td>{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Data</b></td><td>{req.data.strftime("%d/%m/%Y")} às {req.horario.strftime("%H:%M")}</td></tr>
      <tr><td><b>Orientador</b></td><td>{req.orientador.name}</td></tr>
    </table>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""


def build_rejection_subject(req: BancaRequest) -> str:
    return f"[SigBah!] Pedido de Banca #{req.ata} rejeitado — {req.nome.name}"


def build_rejection_html(req: BancaRequest, reason: str) -> str:
    return f"""\
<html>
  <body>
    <h2>Pedido de Banca Rejeitado — SigBah!</h2>
    <p>Seu pedido de banca foi rejeitado pelo coordenador.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td>{req.nome.name}</td></tr>
      <tr><td><b>Tipo</b></td><td>{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Número da Ata</b></td><td>{req.ata}</td></tr>
    </table>
    <h3>Motivo</h3>
    <blockquote style="border-left: 3px solid #fca5a5; padding: 0.5rem 1rem; margin: 0.5rem 0; background: #fef2f2;">
      {reason}
    </blockquote>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""
