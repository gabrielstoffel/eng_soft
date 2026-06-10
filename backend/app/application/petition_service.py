from html import escape

from app.config.ppg_profiles import PpgProfile
from app.domain.models import BancaRequest, MemberInfo

_TIPO_LABEL = {
    1: "Dissertação de Mestrado",
    2: "Exame de Qualificação ao Doutorado",
    3: "Tese de Doutorado",
}

_MODALIDADE_LABEL = {
    "presencial": "Presencial",
    "hibrida": "Híbrida",
    "remota": "Remota",
}


def tipo_label(tipo: int) -> str:
    return _TIPO_LABEL[tipo]


def build_petition_subject(req: BancaRequest, ata: int) -> str:
    return f"[SigBah!] Novo Pedido de Banca #{ata} — {req.nome.name}"


_DECISION_BUTTON_STYLE = (
    "display:inline-block;padding:10px 20px;background:#3b82f6;"
    "color:#fff;text-decoration:none;border-radius:4px;font-weight:600;"
)


def build_petition_html(req: BancaRequest, decision_link: str) -> str:
    """Email to coordenador — no date/location, includes commentary fields."""
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
        remoto_badge = ' <span style="color:#6366f1;">(remoto)</span>' if member.remoto else ""
        membros_rows += f"<tr><td><b>{label}</b></td><td>{escape(member.name)}{remoto_badge}</td><td>{escape(member.institution)}</td></tr>\n"

    comentario_section = ""
    if req.comentario_desempenho:
        comentario_section += f"""
    <h3>Comentários sobre o desempenho do estudante</h3>
    <blockquote style="border-left:3px solid #93c5fd;padding:0.5rem 1rem;margin:0.5rem 0;background:#eff6ff;">
      {escape(req.comentario_desempenho)}
    </blockquote>"""
    if req.justificativa_membros:
        comentario_section += f"""
    <h3>Justificativa para a escolha dos membros</h3>
    <blockquote style="border-left:3px solid #93c5fd;padding:0.5rem 1rem;margin:0.5rem 0;background:#eff6ff;">
      {escape(req.justificativa_membros)}
    </blockquote>"""

    titulo2_row = ""
    if req.titulo2:
        titulo2_row = f'<tr><td><b>Title (EN)</b></td><td colspan="2">{escape(req.titulo2)}</td></tr>'

    return f"""\
<html>
  <body>
    <h2>Novo Pedido de Banca — SigBah!</h2>
    <p>Uma nova banca foi submetida e aguarda sua decisão.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td colspan="2">{escape(req.nome.name)}</td></tr>
      <tr><td><b>Tipo</b></td><td colspan="2">{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Título (PT)</b></td><td colspan="2">{escape(req.titulo)}</td></tr>
      {titulo2_row}
    </table>
    <h3>Membros da Banca</h3>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>Função</th><th>Nome</th><th>Instituição</th></tr>
      {membros_rows}
    </table>
    {comentario_section}
    <p style="margin-top:1.5rem;">
      <a href="{decision_link}" style="{_DECISION_BUTTON_STYLE}">Acessar página de decisão</a>
    </p>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""


def build_documents_html(req: BancaRequest, ata: int, observation: str | None = None) -> str:
    obs_section = ""
    if observation:
        obs_section = f"""
    <h3>Observação do coordenador</h3>
    <blockquote style="border-left:3px solid #fbbf24;padding:0.5rem 1rem;margin:0.5rem 0;background:#fffbeb;">
      {escape(observation)}
    </blockquote>"""

    return f"""\
<html>
  <body>
    <h2>Documentos da Banca #{ata} — SigBah!</h2>
    <p>Os documentos foram gerados e estão em anexo (arquivo zip).</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td>{escape(req.nome.name)}</td></tr>
      <tr><td><b>Tipo</b></td><td>{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Data</b></td><td>{req.data.strftime("%d/%m/%Y")} às {req.horario.strftime("%H:%M")}</td></tr>
      <tr><td><b>Orientador</b></td><td>{escape(req.orientador.name)}</td></tr>
    </table>
    {obs_section}
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""


def build_gerencia_html(req: BancaRequest, ata: int, profile: PpgProfile) -> str:
    sala = escape(req.sala_preferencia) if req.sala_preferencia else "—"
    return f"""\
<html>
  <body>
    <h2>Solicitação de Agendamento — SigBah!</h2>
    <p>Uma banca foi aprovada e requer agendamento de sala.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Banca</b></td><td>#{ata}</td></tr>
      <tr><td><b>Tipo</b></td><td>{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Data sugerida</b></td><td>{req.data.strftime("%d/%m/%Y")} às {req.horario.strftime("%H:%M")}</td></tr>
      <tr><td><b>Local de preferência</b></td><td>{sala}</td></tr>
      <tr><td><b>Modalidade</b></td><td>{_MODALIDADE_LABEL.get(req.modalidade, req.modalidade)}</td></tr>
      <tr><td><b>Aluno</b></td><td>{escape(req.nome.name)}</td></tr>
      <tr><td><b>Orientador</b></td><td>{escape(req.orientador.name)}</td></tr>
    </table>
    <p>Solicitamos o agendamento da sala. Favor responder para <b>{profile.cpg_alias_email}</b>.</p>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""


def build_invite_subject(req: BancaRequest, ata: int, kind: str) -> str:
    doc = "Carta-convite" if kind == "carta_convite" else "Solicitação de parecer"
    return f"[SigBah!] {doc} — Banca #{ata} ({req.nome.name})"


def build_invite_html(req: BancaRequest, ata: int, kind: str, member: MemberInfo) -> str:
    if kind == "carta_convite":
        intro = (
            "Segue em anexo a carta-convite para sua participação na banca examinadora "
            "abaixo. Agradecemos a atenção."
        )
    else:
        intro = (
            "Segue em anexo o formulário de parecer referente à banca examinadora abaixo. "
            "Solicitamos a gentileza de preenchê-lo e devolvê-lo à secretaria."
        )
    return f"""\
<html>
  <body>
    <h2>{("Carta-convite" if kind == "carta_convite" else "Solicitação de parecer")} — SigBah!</h2>
    <p>Prezado(a) {escape(member.name)},</p>
    <p>{intro}</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Banca</b></td><td>#{ata}</td></tr>
      <tr><td><b>Aluno</b></td><td>{escape(req.nome.name)}</td></tr>
      <tr><td><b>Tipo</b></td><td>{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Data sugerida</b></td><td>{req.data.strftime("%d/%m/%Y")} às {req.horario.strftime("%H:%M")}</td></tr>
    </table>
    <p>Atenciosamente,<br>Secretaria — Sistema SigBah!</p>
  </body>
</html>
"""


def build_rejection_subject(req: BancaRequest, ata: int) -> str:
    return f"[SigBah!] Pedido de Banca #{ata} rejeitado — {req.nome.name}"


def build_rejection_html(req: BancaRequest, ata: int, reason: str) -> str:
    return f"""\
<html>
  <body>
    <h2>Pedido de Banca Rejeitado — SigBah!</h2>
    <p>Seu pedido de banca foi rejeitado pelo coordenador.</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><td><b>Aluno</b></td><td>{escape(req.nome.name)}</td></tr>
      <tr><td><b>Tipo</b></td><td>{tipo_label(req.tipo)}</td></tr>
      <tr><td><b>Número da Ata</b></td><td>{ata}</td></tr>
    </table>
    <h3>Motivo</h3>
    <blockquote style="border-left:3px solid #fca5a5;padding:0.5rem 1rem;margin:0.5rem 0;background:#fef2f2;">
      {escape(reason)}
    </blockquote>
    <p>Atenciosamente,<br>Sistema SigBah!</p>
  </body>
</html>
"""
