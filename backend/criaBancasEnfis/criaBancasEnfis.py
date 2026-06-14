"""ppgenfis (Programa de Pós-Graduação em Ensino de Física) document generator.

Python port of the legacy `cria_cartas.php`, which produced the cartas-convite
(invitation letters) for a banca examinadora of the Ensino de Física program.

The class mirrors the `criaBancas.Banca` interface used by the ppgfis program so
that `app.application.document_service` can drive either generator with the same
construction kwargs and the same `criaCartaConvite(save=True)` call:

  * identical constructor signature (raw `(gender, name, institution, location,
    lang)` member tuples — titles are added inline here, not pre-applied);
  * identical `tipo` convention: 1 = Mestrado, 2 = Qualificação, 3 = Doutorado;
  * `criaCartaConvite(save=True)` writes ONE PDF per member (the PHP emitted a
    single multi-page document — here the PDFs are split, one file per member);
  * output filenames match `criaBancas`: "Carta Convite {FUNCAO} - {nome}.pdf".

Fonts and the Instituto de Física logo are reused from the sibling `criaBancas`
asset folder to avoid duplicating ~30 font files. The legacy PHP used Garamond
(body) and Georgia (letterhead); both are serif, so Cambria is used as the
substitute here.
"""

import os
from datetime import date, time

import qrcode
from fpdf import FPDF, XPos, YPos

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Reuse the ppgfis asset folder (fonts + IF logo) instead of duplicating it.
_ASSETS_DIR = os.path.join(_BASE_DIR, "..", "criaBancas")
_FONTS_DIR = os.path.join(_ASSETS_DIR, "Fonts")
_LOGO_IF = os.path.join(_ASSETS_DIR, "logo-if-small.png")

# Member role -> internal "tipo". The PHP `banca.tipo` column only knew
# presidente/titular/suplente; coorientador is a SigBah addition ("acompanhar"),
# modelled here on criaBancas.
#   1 = presidente   (orientador, "presidir")
#   2 = suplente     ("compor, na condição de membro suplente,")
#   3 = coorientador ("acompanhar" — não julga, não consta da lista de membros)
#   0 = titular      (everyone else, "compor")
_PRESIDENTE = 1
_SUPLENTE = 2
_COORIENTADOR = 3
_TITULAR = 0

# Role -> FUNCAO token used in the output filename (matches criaBancas).
_FUNCAO_FILENAME = {
    "orientador": "ORIENTADOR",
    "coorientador": "COORIENTADOR",
    "externo1": "TITULAR",
    "externo2": "TITULAR",
    "interno1": "TITULAR",
    "interno2": "TITULAR",
    "supl_int": "SUPLENTE",
    "supl_ext": "SUPLENTE",
}

_MESES = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}


def _mes_extenso(mes: int) -> str:
    return _MESES.get(mes, "")


class _PDF(FPDF):
    def center(self, w: float) -> float:
        return (210 - w) / 2


class Banca:
    # Document roles, in display order. Mirrors criaBancas.criaCartaConvite.
    _ROLES = (
        "orientador",
        "coorientador",
        "externo1",
        "externo2",
        "interno1",
        "interno2",
        "supl_int",
        "supl_ext",
    )

    def __init__(
        self,
        nome,
        tipo: int,
        horario: time,
        data: date,
        data_convite: date,
        ata: int,
        local_banca: str,
        link: str,
        orientador,
        coorientador,
        externo1,
        externo2,
        interno1,
        interno2,
        supl_int,
        supl_ext,
        titulo: str,
        titulo2: str,
        data_parecer: date | None = None,
    ):
        self.nome = nome
        self.tipo = tipo
        self.horario = horario
        self.data = data
        self.data_convite = data_convite if data_convite is not None else data
        self.ata = ata
        self.local_banca = local_banca
        self.link = link
        self.orientador = orientador
        self.coorientador = coorientador
        self.externo1 = externo1
        self.externo2 = externo2
        self.interno1 = interno1
        self.interno2 = interno2
        self.supl_int = supl_int
        self.supl_ext = supl_ext
        self.titulo = titulo
        self.titulo2 = titulo2
        # Data de envio do parecer (PHP: POST dia/mes/ano_parecer). Passada pela
        # interface; cai na data da defesa apenas se não for informada.
        self.data_parecer = data_parecer if data_parecer is not None else data

        self.dir = os.path.join(_BASE_DIR, "Bancas", f"{self.ata} - {self.nome[1]}")
        os.makedirs(self.dir, exist_ok=True)

        self.pdf = self._new_pdf()

    # --- helpers -------------------------------------------------------------

    def _new_pdf(self) -> _PDF:
        pdf = _PDF()
        pdf.alias_nb_pages()
        pdf.add_font("Cambria", "", os.path.join(_FONTS_DIR, "cambria.ttc"))
        pdf.add_font("Cambria", "B", os.path.join(_FONTS_DIR, "cambriab.ttf"))
        pdf.add_font("Cambria", "I", os.path.join(_FONTS_DIR, "cambriai.ttf"))
        return pdf

    def _descricao_trabalho(self) -> str:
        match self.tipo:
            case 1:
                return "Dissertação de Mestrado"
            case 2:
                return "Exame de Qualificação para Doutorado"
            case 3:
                return "Tese de Doutorado"
        return ""

    def _tipo_membro(self, role: str) -> int:
        if role == "orientador":
            return _PRESIDENTE
        if role == "coorientador":
            return _COORIENTADOR
        if role in ("supl_int", "supl_ext"):
            return _SUPLENTE
        return _TITULAR

    @staticmethod
    def _titulo_pessoa(membro) -> str:
        """'Prof. Dr. Nome' / 'Profa. Dra. Nome' from a (gender, name, ...) tuple."""
        prefixo = "Profa. Dra. " if membro[0] else "Prof. Dr. "
        return prefixo + membro[1]

    def _sob_orientacao(self) -> str:
        """'sob orientação do Prof. Dr. X (e da Profa. Dra. Y)' — orientador only.

        The legacy form carried a free-text second advisor; here the optional
        coorientador role fills that slot when present.
        """
        partes = []
        if self.orientador is not None:
            artigo = "da" if self.orientador[0] else "do"
            partes.append(f"sob orientação {artigo} {self._titulo_pessoa(self.orientador)}")
        if self.coorientador is not None:
            artigo = "da" if self.coorientador[0] else "do"
            partes.append(f"{artigo} {self._titulo_pessoa(self.coorientador)}")
        if len(partes) == 2:
            return partes[0] + " e " + partes[1]
        return partes[0] if partes else ""

    # --- header (PHP fazHeader) ---------------------------------------------

    def _header(self) -> None:
        pdf = self.pdf
        header_margin = 30

        if os.path.exists(_LOGO_IF):
            pdf.image(_LOGO_IF, x=25, y=20, w=22, h=22)

        pdf.set_y(20)
        pdf.set_font("Cambria", "B", 12)
        pdf.set_x(25 + header_margin)
        pdf.cell(0, 8, "Instituto de Física - UFRGS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_x(25 + header_margin)
        pdf.cell(0, 4, "_" * 43, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        pdf.set_font("Cambria", "", 12)
        pdf.set_x(25 + header_margin)
        pdf.cell(
            0, 6, "Programa de Pós-Graduação em Ensino de Física",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )

        pdf.set_font("Cambria", "", 10)
        for linha in (
            "Caixa Postal 15051 - 91501-970 Porto Alegre, RS, Brasil",
            "Tel.: (55)(51) 3308-6431 - FAX: (55)(51) 3308-7286",
            "e-mail: ppgenfis@if.ufrgs.br",
        ):
            pdf.set_x(25 + header_margin)
            pdf.cell(0, 5, linha, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(20)
        pdf.set_font("Cambria", "", 12)
        dc = self.data_convite
        pdf.cell(
            0, 8,
            f"Porto Alegre, {dc.day} de {_mes_extenso(dc.month)} de {dc.year}.",
            align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        pdf.ln(8)

    # --- corpo (PHP paragrafo_1) --------------------------------------------

    def _paragrafo_convite(self, role: str) -> str:
        tipo_membro = self._tipo_membro(role)
        if tipo_membro == _PRESIDENTE:
            funcao = "presidir"
            demais = "Os demais membros da Banca Examinadora são"
        elif tipo_membro == _SUPLENTE:
            funcao = "compor, na condição de membro suplente,"
            demais = "Os membros titulares da Banca Examinadora são"
        elif tipo_membro == _COORIENTADOR:
            funcao = "acompanhar"
            demais = "Os membros da Banca Examinadora são"
        else:
            funcao = "compor"
            demais = "Os demais membros da Banca Examinadora são"

        aluno = self.nome[1]
        descricao = self._descricao_trabalho()
        sob_orientacao = self._sob_orientacao()
        abertura = (
            "É com satisfação que, em nome da Comissão Coordenadora do Programa de "
            "Pós-Graduação em Ensino de Física da Universidade Federal do Rio Grande "
            f"do Sul, convido V. Sa. para {funcao} a Banca Examinadora "
        )

        if self.tipo == 2:  # Exame de Qualificação ("intitulado", artigo "do")
            return (
                abertura
                + f'do {descricao} de {aluno}, intitulado "{self.titulo}". '
                f"Esse doutorando desenvolve sua tese {sob_orientacao}. {demais}:"
            )
        # Mestrado / Doutorado ("intitulada", artigo "da")
        return (
            abertura
            + f'da {descricao} de {aluno}, intitulada "{self.titulo}", '
            f"{sob_orientacao}. {demais}:"
        )

    def _data_parecer_str(self) -> str:
        dp = self.data_parecer
        return f"{dp.day:02d}/{dp.month:02d}/{dp.year}"

    # --- carta-convite -------------------------------------------------------

    def criaCartaConvite(self, save: bool = False) -> None:
        for role in self._ROLES:
            membro = getattr(self, role)
            if membro is None:
                continue

            if save is True:
                self.pdf = self._new_pdf()

            pdf = self.pdf
            pdf.set_auto_page_break(True, margin=15)
            pdf.set_left_margin(25)
            pdf.set_right_margin(25)
            pdf.add_page("P")
            self._header()

            tipo_membro = self._tipo_membro(role)

            # Saudação ------------------------------------------------------
            pdf.set_font("Cambria", "", 12)
            if membro[0]:  # feminino
                pdf.cell(0, 6, "Ilma. Sra.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                pdf.cell(0, 6, "Ilmo. Sr.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Cambria", "B", 12)
            pdf.cell(0, 6, self._titulo_pessoa(membro), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Cambria", "", 12)
            pdf.cell(0, 6, membro[2], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(6)
            pdf.cell(
                0, 6,
                "Prezada Senhora:" if membro[0] else "Prezado Senhor:",
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.ln(6)

            # Parágrafo de convite -----------------------------------------
            pdf.multi_cell(0, 5, self._paragrafo_convite(role), align="J")
            pdf.ln(3)

            # Lista dos membros da banca: apenas titulares + presidente. Exclui
            # o próprio destinatário, os suplentes e o coorientador (que apenas
            # acompanha, não compõe a banca). -----------------------------
            for outro_role in self._ROLES:
                if outro_role == role:
                    continue
                outro = getattr(self, outro_role)
                if outro is None or self._tipo_membro(outro_role) not in (_TITULAR, _PRESIDENTE):
                    continue
                pdf.set_x(35)
                pdf.set_font("Cambria", "B", 12)
                pdf.cell(pdf.get_string_width("- " + self._titulo_pessoa(outro)) + 1, 7,
                         "- " + self._titulo_pessoa(outro))
                pdf.set_font("Cambria", "", 12)
                pdf.cell(0, 7, f" ({outro[2]})", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(3)

            # Corpo final (parágrafo de parecer — só Mestrado) --------------
            paragrafo_2 = None
            if self.tipo == 1:
                if tipo_membro == _PRESIDENTE:
                    paragrafo_2 = (
                        "Conforme estabelece a legislação da Pós-graduação da UFRGS, o(a) "
                        "orientador(a) atua como presidente da Banca Examinadora, sem "
                        "direito a julgamento."
                    )
                elif tipo_membro in (_TITULAR, _SUPLENTE):
                    paragrafo_2 = (
                        "A aprovação ou reprovação desta dissertação deverá ser baseada em "
                        "parecer individual dos membros da Banca, encaminhados à Comissão "
                        "Coordenadora, via correio eletrônico (ppgenfis@if.ufrgs.br) ou "
                        "entregue diretamente na secretaria do Programa, no máximo até o dia "
                        f"{self._data_parecer_str()}. Uma vez que a dissertação esteja "
                        "aprovada pelos membros da banca, haverá a apresentação pública da "
                        "mesma na qual cada membro da Banca Examinadora atribuirá o conceito "
                        "final igual ou superior a C, para a aprovação."
                    )
                # coorientador apenas acompanha — não recebe parágrafo de parecer.
            if paragrafo_2 is not None:
                pdf.set_font("Cambria", "", 12)
                pdf.multi_cell(0, 5, paragrafo_2, align="J")
                pdf.ln(3)

            self._corpo_final(tipo_membro)

            if save is True:
                funcao_arquivo = _FUNCAO_FILENAME[role]
                # Filename mirrors the document_service manifest label, which
                # prefixes the member's name with the same title abbreviation
                # criaBancas uses (note the superscript ª/º) — keep them in sync.
                prefixo = "Profª. Drª. " if membro[0] else "Prof. Dr. "
                self.pdf.output(
                    os.path.join(self.dir, f"Carta Convite {funcao_arquivo} - {prefixo}{membro[1]}.pdf")
                )

    def _corpo_final(self, tipo_membro: int) -> None:
        pdf = self.pdf
        pdf.set_font("Cambria", "", 12)

        dia = self.data.day
        mes = _mes_extenso(self.data.month)
        ano = self.data.year
        data_hora = (
            f"Data e horário: {dia} de {mes} de {ano}, "
            f"às {self.horario.hour}h{self.horario.minute:02d}min"
        )

        if tipo_membro == _SUPLENTE:
            pdf.cell(0, 6, "Entraremos em contato caso sua presença seja necessária.",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(4)
            pdf.cell(0, 6, "Aproveito a oportunidade para apresentar a V.Sa.",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(6)
            pdf.cell(0, 6, "Cordiais saudações,", align="C")
            return

        if tipo_membro == _TITULAR:
            pdf.multi_cell(
                0, 6,
                "Conforme estabelece a legislação da Pós-graduação da UFRGS, o(a) "
                "orientador(a) atua como presidente da Banca Examinadora, sem direito "
                "a julgamento.",
                align="L",
            )
            pdf.ln(2)

        pdf.cell(0, 6, data_hora, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if self.local_banca is not None:
            pdf.cell(0, 6, f"Local: {self.local_banca}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if self.link is not None:
            pdf.cell(0, 6, f"Link: {self.link}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if self.tipo == 1 and tipo_membro == _TITULAR:
            pdf.ln(6)
            pdf.multi_cell(
                0, 6,
                "Esperando que V.Sa. aceite esse convite e encaminhe o parecer "
                f"individual até {self._data_parecer_str()},",
                align="L",
            )

        pdf.ln(6)
        pdf.cell(0, 6, "Cordiais saudações,", align="C")

    # --- parecer (folha de conceito) ----------------------------------------

    def criaParecer(self, save: bool = False) -> None:
        """One "folha de conceito" PDF per voting member (externos + internos).

        Mirrors criaBancas.criaParecer, but follows the ppgenfis template
        (documentation/ppgenfis/"Folha de conceito em word.docx"): a fill-in
        "conceito ______" blank plus a free-text "Comentários" block, instead of
        the ppgfis checkbox grid. Portuguese only.
        """
        for membro in (self.externo1, self.externo2, self.interno1, self.interno2):
            if membro is None:
                continue

            if save is True:
                self.pdf = self._new_pdf()

            pdf = self.pdf
            pdf.set_auto_page_break(True, margin=15)
            pdf.set_left_margin(25)
            pdf.set_right_margin(25)
            pdf.add_page("P")

            # Data (data da defesa), alinhada à direita -------------------
            pdf.set_y(40)
            pdf.set_font("Cambria", "", 12)
            d = self.data
            pdf.cell(
                0, 6,
                f"Porto Alegre, {d.day} de {_mes_extenso(d.month)} de {d.year}.",
                align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.ln(20)

            # Título do trabalho ----------------------------------------
            pdf.set_font("Cambria", "B", 16)
            pdf.cell(
                0, 8, self._descricao_trabalho().upper(),
                align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.ln(16)

            # Autor(a) + título -----------------------------------------
            autor = "Autora" if self.nome[0] else "Autor"
            pdf.set_font("Cambria", "", 13)
            pdf.multi_cell(
                0, 7,
                f"{autor}: **{self.nome[1]}**\n\nTítulo: __{self.titulo}__",
                align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.ln(16)

            # Declaração + conceito -------------------------------------
            pdf.set_font("Cambria", "", 13)
            pdf.multi_cell(
                0, 7,
                "DECLARO que examinei o trabalho em epígrafe, atribuindo-lhe "
                "conceito ______________.",
                align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.set_font("Cambria", "I", 11)
            pdf.cell(0, 6, "(Aprovado ou Reprovado).", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(12)

            # Comentários -----------------------------------------------
            pdf.set_font("Cambria", "", 13)
            pdf.cell(0, 7, "Comentários:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(45)

            # Assinatura ------------------------------------------------
            nome_assinatura = self._titulo_pessoa(membro)
            largura = pdf.get_string_width(nome_assinatura)
            x = pdf.center(largura)
            y = pdf.get_y()
            pdf.line(x, y, x + largura, y)
            pdf.ln(2)
            pdf.set_font("Cambria", "B", 12)
            pdf.cell(0, 6, nome_assinatura, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Cambria", "", 12)
            pdf.cell(0, 6, membro[2], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            if save is True:
                # Filename mirrors the document_service parecer manifest label.
                prefixo = "Profª. Drª. " if membro[0] else "Prof. Dr. "
                self.pdf.output(os.path.join(self.dir, f"Parecer - {prefixo}{membro[1]}.pdf"))

    # --- cartaz (divulgação) -------------------------------------------------

    def criaCartaz(self, save: bool = False) -> None:
        """Single landscape poster advertising the defense.

        Mirrors criaBancas.criaCartaz, following the ppgenfis template
        (documentation/ppgenfis/cartaz.docx): only the Portuguese title is shown
        and the board members are bulleted with their institutions. A QR code for
        the videoconference link is embedded in the footer when a link is set.
        """
        if save is True:
            self.pdf = self._new_pdf()

        pdf = self.pdf
        pdf.add_page(orientation="L")
        pdf.set_auto_page_break(False)
        margin = 25
        pdf.set_left_margin(margin)
        pdf.set_right_margin(margin)
        page_w = pdf.w

        if os.path.exists(_LOGO_IF):
            pdf.image(_LOGO_IF, x=margin, y=12, w=20, h=20)

        # Título (tipo de trabalho) ------------------------------------
        pdf.set_y(18)
        pdf.set_font("Cambria", "B", 26)
        pdf.multi_cell(
            0, 12, self._descricao_trabalho().upper(),
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT, wrapmode="WORD",
        )
        pdf.ln(8)

        # Autor(a) ------------------------------------------------------
        autor = "AUTORA" if self.nome[0] else "AUTOR"
        pdf.set_font("Cambria", "", 20)
        pdf.cell(
            0, 10, f"{autor}: **{self.nome[1]}**",
            align="C", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        pdf.ln(6)

        # Título do trabalho -------------------------------------------
        pdf.set_font("Cambria", "", 16)
        pdf.multi_cell(
            0, 8, f"TÍTULO: **“{self.titulo}”**",
            align="C", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT, wrapmode="WORD",
        )
        pdf.ln(10)

        # Orientação ----------------------------------------------------
        pdf.set_font("Cambria", "", 13)
        pdf.cell(
            0, 7, f"ORIENTADOR: **{self._titulo_pessoa(self.orientador)}**",
            align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        if self.coorientador is not None:
            pdf.cell(
                0, 7, f"COORIENTADOR: **{self._titulo_pessoa(self.coorientador)}**",
                align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
        pdf.ln(6)

        # Banca examinadora --------------------------------------------
        pdf.cell(0, 7, "**Banca Examinadora:**", align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)
        for membro in (self.externo1, self.externo2, self.interno1, self.interno2):
            if membro is None:
                continue
            pdf.set_x(margin + 8)
            pdf.multi_cell(
                0, 7, f"● {self._titulo_pessoa(membro)} ({membro[2]})",
                align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )

        # Rodapé: data, horário, local, link + QR ----------------------
        pdf.set_y(-45)
        pdf.line(margin, pdf.get_y(), page_w - margin, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("Cambria", "", 13)
        half = (page_w - 2 * margin) / 2
        pdf.cell(
            half, 7,
            f"DATA: **{self.data.day} de {_mes_extenso(self.data.month)} de {self.data.year}**",
            align="L", markdown=True,
        )
        pdf.cell(
            half, 7,
            f"HORÁRIO: **{self.horario.hour}h{self.horario.minute:02d}min**",
            align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        if self.local_banca is not None:
            pdf.cell(
                0, 7, f"LOCAL: **{self.local_banca}**",
                align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
        if self.link is not None:
            pdf.cell(
                0, 7, f"LINK: **{self.link}**",
                align="L", markdown=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(self.link)
            qr.make(fit=True)
            qr_path = os.path.join(_BASE_DIR, "qrcode.png")
            qr.make_image().save(qr_path)
            # A4 landscape height is 210mm; anchor the QR above the bottom edge.
            pdf.image(qr_path, x=page_w - margin - 25, y=210 - 30, w=25, h=25)

        if save is True:
            self.pdf.output(os.path.join(self.dir, f"Cartaz - {self.nome[1]}.pdf"))
