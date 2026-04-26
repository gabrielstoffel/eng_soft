import os
import sys
from datetime import date, datetime, time

import qrcode
from fpdf import FPDF, XPos, YPos

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class PDF(FPDF):
    def center(self, w):
        width = 210
        if self.cur_orientation == "L":
            width = 297

        return (width - w) / 2

    def get_page_width(self):
        if self.cur_orientation == "L":
            return 297
        return 210

    def header(self):
        alt = 7
        centerImg_x = PDF.center(self, w=80)
        space = 25
        if self.cur_orientation == "L":
            space = 25
            size = 25
            ajust = 5
        else:
            space = 20
            size = 20
            ajust = 0

        space_between_imgs = centerImg_x - space - 20
        self.image(
            os.path.join(_BASE_DIR, "logo-ufrgs-small.png"),
            x=space,
            y=alt,
            w=size,
            h=size,
        )
        self.image(
            os.path.join(_BASE_DIR, "logo-ppgfis-small.png"),
            x=centerImg_x,
            y=alt + ajust,
            w=80,
            h=20,
        )
        self.image(
            os.path.join(_BASE_DIR, "logo-if-small.png"),
            x=centerImg_x + 80 + space_between_imgs,
            y=alt,
            w=size,
            h=size,
        )
        space_imgs_line = 4
        self.line(
            space + 10,
            alt + size + space_imgs_line,
            self.get_page_width() - (space + 10),
            alt + size + space_imgs_line,
        )
        self.set_top_margin(space + 10)

    def footer(self):
        if self.cur_orientation == "L":
            return

        alt = 283
        margin = 15
        self.set_y(-margin)
        self.set_auto_page_break(True, margin)

        self.set_font("Federo", "", 8)

        s = "PROGRAMA DE PÓS-GRADUAÇÃO EM FÍSICA – INSTITUTO DE FÍSICA - UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL"
        s_size = self.get_string_width(s)
        self.line(PDF.center(self, s_size), alt, s_size + PDF.center(self, s_size), alt)

        self.set_text_color(0, 0, b=200)
        self.cell(0, 10, s, align="C")
        self.ln(3)
        self.cell(
            0,
            10,
            "Av. Bento Gonçalves, 9500 - Prédio 43.176 – Sala 204 - Campus do Vale - Caixa Postal 15051 – CEP 91501-970 - Porto Alegre/RS",
            align="C",
        )
        self.ln(h=3)
        self.cell(
            0,
            10,
            "Fone: (55) (51) 3308.6435         Homepage:  https://www.if.ufrgs.br/if/ppgfis/           E-mail:  cpgfis@if.ufrgs.br",
            align="C",
        )


class Banca:
    def __init__(
        self,
        nome: str,
        tipo: int,
        horario: time,
        data: date,
        data_convite: date,
        ata: int,
        local_banca: str,
        link: str,
        orientador: (int, str, str),
        coorientador: (int, str, str),
        externo1: (int, str, str),
        externo2: (int, str, str),
        interno1: (int, str, str),
        interno2: (int, str, str),
        supl_int: (int, str, str),
        supl_ext: (int, str, str),
        titulo: str,
        titulo2: str,
    ):
        self.nome = nome
        self.tipo = tipo
        self.horario = horario
        self.data = data
        self.data_convite = data_convite
        if self.data_convite is None:
            self.data_convite = data
        self.ata = ata
        self.local_banca = local_banca
        self.link = link
        self.orientador = self.tratamentoAta(orientador)
        self.coorientador = self.tratamentoAta(coorientador)
        self.externo1 = self.tratamentoAta(externo1)
        self.externo2 = self.tratamentoAta(externo2)
        self.interno1 = self.tratamentoAta(interno1)
        self.interno2 = self.tratamentoAta(interno2)
        self.supl_int = self.tratamentoAta(supl_int)
        self.supl_ext = self.tratamentoAta(supl_ext)
        self.titulo = titulo
        self.titulo2 = titulo2
        self.dir = f"{self.ata} - {self.nome[1]}"
        self.dir = os.path.join(_BASE_DIR, "Bancas", self.dir)
        os.makedirs(self.dir, exist_ok=True)

        self.pdf = PDF()
        self.pdf.alias_nb_pages()
        self.pdf.add_font("Federo", "", os.path.join(_BASE_DIR, "Fonts", "Federo-Regular.ttf"))
        self.pdf.add_font("Verdana", "", os.path.join(_BASE_DIR, "Fonts", "verdana.ttf"))
        self.pdf.add_font("Verdana", "B", os.path.join(_BASE_DIR, "Fonts", "verdanab.ttf"))
        self.pdf.add_font("Verdana", "I", os.path.join(_BASE_DIR, "Fonts", "verdanai.ttf"))
        self.pdf.add_font("Verdana", "BI", os.path.join(_BASE_DIR, "Fonts", "verdanaz.ttf"))
        self.pdf.add_font("calibri", "", os.path.join(_BASE_DIR, "Fonts", "calibri.ttf"))
        self.pdf.add_font("calibri", "B", os.path.join(_BASE_DIR, "Fonts", "calibrib.ttf"))
        self.pdf.add_font("calibri", "I", os.path.join(_BASE_DIR, "Fonts", "calibrii.ttf"))
        self.pdf.add_font("calibri", "BI", os.path.join(_BASE_DIR, "Fonts", "calibriz.ttf"))
        self.pdf.add_font("cambria", "", os.path.join(_BASE_DIR, "Fonts", "cambria.ttc"))
        self.pdf.add_font("cambria", "B", os.path.join(_BASE_DIR, "Fonts", "cambriab.ttf"))
        self.pdf.add_font("cambria", "I", os.path.join(_BASE_DIR, "Fonts", "cambriai.ttf"))
        self.pdf.add_font("cambria", "BI", os.path.join(_BASE_DIR, "Fonts", "cambriaz.ttf"))
        self.pdf.add_font("Arial", "", os.path.join(_BASE_DIR, "Fonts", "arial.ttf"))
        self.pdf.add_font("Arial", "B", os.path.join(_BASE_DIR, "Fonts", "arialbd.ttf"))

    def tipoAta(self, tipo):
        texto = ""
        match tipo:
            case 1:
                texto = "Dissertação de Mestrado"
            case 2:
                texto = "Exame de Qualificação ao Doutorado"
            case 3:
                texto = "Tese de Doutorado"
        return texto

    def tipoAtaEn(self, tipo):
        texto = ""
        match self.tipo:
            case 1:
                texto = "Master's Dissertation"
            case 2:
                texto = "Doctoral Qualifying Exam"
            case 3:
                texto = "Doctoral Exam"
        return texto

    def tratamentoAta(self, name):
        if name is None:
            return name

        texto = None
        match name[0]:
            case 0:
                texto = "Prof. Dr. "
            case 1:
                texto = "Profª. Drª. "
        return [name[0], texto + name[1], name[2], name[3], name[4]]

    def dataMesExtenso(self, mes):
        meses_por_extenso = {
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
        return meses_por_extenso.get(mes)

    def dataMesExtenso_en(self, mes):
        meses_por_extenso = {
            1: "january",
            2: "february",
            3: "march",
            4: "april",
            5: "may",
            6: "june",
            7: "july",
            8: "august",
            9: "setember",
            10: "october",
            11: "november",
            12: "december",
        }
        return meses_por_extenso.get(mes)

    def dataExtenso(self, data):
        numeros_por_extenso = {
            1: "um",
            2: "dois",
            3: "três",
            4: "quatro",
            5: "cinco",
            6: "seis",
            7: "sete",
            8: "oito",
            9: "nove",
            10: "dez",
            11: "onze",
            12: "doze",
            13: "treze",
            14: "catorze",
            15: "quinze",
            16: "dezesseis",
            17: "dezessete",
            18: "dezoito",
            19: "dezenove",
            20: "vinte",
            30: "trinta",
            40: "quarenta",
            50: "cinquenta",
            60: "sessenta",
            70: "setenta",
            80: "oitenta",
            90: "noventa",
        }

        dia = data.day
        mes = data.month
        ano = data.year

        texto = []
        if dia <= 20 or dia == 30:
            texto.append(numeros_por_extenso.get(dia, str(dia)))
        elif dia <= 31:
            dezena = (dia // 10) * 10
            unidade = dia % 10
            # print(f"dia={dia} dezena={dezena} unidade={unidade}")
            texto.append(numeros_por_extenso.get(dezena) + " e " + numeros_por_extenso.get(unidade))
        texto.append("de " + self.dataMesExtenso(mes))
        # print(texto)

        if ano <= 2099:
            dezena = ((ano % 2000) // 10) * 10
            unidade = ano % (2000 + dezena)
            # print(f"ano={ano} dezena={dezena} unidade={unidade}")
            texto.append("de dois mil e " + numeros_por_extenso.get(dezena) + " e " + numeros_por_extenso.get(unidade))
        # print(texto)

        return " ".join(texto)

    def trataLocalBanca(self, link, local):
        texto = []
        if link is not None:
            texto.append("via videoconferência através da Sala Virtual")
        if local is not None:
            texto.append(f"n{local.split(' ')[0][-1]} " + local)

        if len(texto) == 2:
            return " e ".join(texto)

        return texto[0]

    def criaAta(self, save=False):
        if self.tipo == 2:
            return

        # Cria ATA
        if save is True:
            self.pdf = PDF()
            self.pdf.alias_nb_pages()
            self.pdf.add_font("Federo", "", os.path.join(_BASE_DIR, "Fonts", "Federo-Regular.ttf"))
            self.pdf.add_font("Verdana", "", os.path.join(_BASE_DIR, "Fonts", "verdana.ttf"))
            self.pdf.add_font("Verdana", "B", os.path.join(_BASE_DIR, "Fonts", "verdanab.ttf"))
            self.pdf.add_font("Verdana", "I", os.path.join(_BASE_DIR, "Fonts", "verdanai.ttf"))
            self.pdf.add_font("calibri", "", os.path.join(_BASE_DIR, "Fonts", "calibri.ttf"))
            self.pdf.add_font("calibri", "B", os.path.join(_BASE_DIR, "Fonts", "calibrib.ttf"))
            self.pdf.add_font("calibri", "I", os.path.join(_BASE_DIR, "Fonts", "calibrii.ttf"))
            self.pdf.add_font("Arial", "", os.path.join(_BASE_DIR, "Fonts", "arial.ttf"))
            self.pdf.add_font("Arial", "B", os.path.join(_BASE_DIR, "Fonts", "arialbd.ttf"))

        self.pdf.add_page()
        margin = 20
        self.pdf.set_left_margin(margin)
        self.pdf.set_right_margin(margin)
        self.pdf.set_auto_page_break(False)
        # Um pouco maior que a margem
        padding = 2
        x_0 = margin - padding
        x_1 = 210 - 2 * x_0
        self.pdf.rect(x_0, 35, x_1, 246, "D")

        self.pdf.set_y(40)
        self.pdf.set_font("calibri", "", 14)

        s = f" Ata {self.ata} - {self.tipoAta(self.tipo)} "
        self.pdf.cell(0, 5, s, align="C")
        self.pdf.ln(10)
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 5, f"{self.nome[1]}", align="C")

        self.pdf.ln(15)
        self.pdf.set_font("Verdana", "", 11)

        artigo = ["O", "A"]
        paragrafo = f"Às ____ h ____  do dia {self.dataExtenso(self.data)}, reuniu-se {self.trataLocalBanca(self.link, self.local_banca)} do Instituto de Física da Universidade Federal do Rio Grande do Sul, a Banca Examinadora, integrada pelos Professores:  **{self.orientador[1]}** (Orientador{'a' if self.orientador[0] else ''}/Presidente - {self.orientador[2]}), **{self.externo1[1]}** ({self.externo1[2]}), "
        if self.tipo == 3:
            paragrafo += f"**{self.externo2[1]}** ({self.externo2[2]}), "
        paragrafo += f"**{self.interno1[1]}** ({self.interno1[2]}) e **{self.interno2[1]}** ({self.interno2[2]}) para dar início à defesa da {self.tipoAta(self.tipo)} de **{self.nome[1]}**, orientad{artigo[self.nome[0]].lower()} pel{artigo[self.orientador[0]].lower()} {self.orientador[1]}, defesa prevista no Regimento do Curso de Pós-Graduação em Física, art. 49. {artigo[self.orientador[0]]} Presidente deu por instalados os trabalhos e convidou {artigo[self.nome[0]].lower()} candidat{artigo[self.nome[0]].lower()} a fazer uma apresentação em forma de Seminário de sua {self.tipoAta(self.tipo).split(' ')[0]} intitulada: __“{self.titulo}” (“{self.titulo2}”)__. A seguir, {artigo[self.nome[0]].lower()} candidat{artigo[self.nome[0]].lower()} respondeu às perguntas formuladas pela Comissão Julgadora e logo após o término da apresentação, os membros da banca se reuniram e julgaram a {self.tipoAta(self.tipo).split(' ')[0]}. Foi divulgado pelo Presidente da banca o resultado atribuído pela comissão julgadora: **{self.externo1[1]}** “parecer em anexo”, "
        if self.tipo == 3:
            paragrafo += f"**{self.externo2[1]}** “parecer em anexo”, "
        paragrafo += f"**{self.interno1[1]}** “parecer em anexo” e **{self.interno2[1]}** “parecer em anexo”. A sessão foi encerrada às ____ h ____ min e para constar, eu, Antonio Levorci Neto, Secretário do Programa de Pós-Graduação em Física, redigi a presente ATA que será assinada pel{artigo[self.orientador[0]].lower()} presidente da Comissão Julgadora."

        self.pdf.multi_cell(0, 6, paragrafo, align="J", markdown=True)
        self.pdf.ln(7)
        assinaturas = f"_______________________ **{self.externo1[1]}**\n"
        if self.tipo == 3:
            assinaturas += f"_______________________ **{self.externo2[1]}**\n"
        assinaturas += f"_______________________ **{self.interno1[1]}**\n_______________________ **{self.interno2[1]}**\n_______________________ **{self.orientador[1]} - Presidente**"
        self.pdf.multi_cell(0, 15, assinaturas, align="L", markdown=True)

        if save is True:
            self.pdf.output(os.path.join(self.dir, "Ata - " + self.nome[1] + ".pdf"))

    # fonte: https://codereview.stackexchange.com/questions/41298/producing-ordinal-numbers
    def ordinalDay(self, day):
        SUFFIXES = {1: "st", 2: "nd", 3: "rd"}
        # I'm checking for 10-20 because those are the digits that
        # don't follow the normal counting scheme.
        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            # the second parameter is a default.
            suffix = SUFFIXES.get(day % 10, "th")
        return str(day) + suffix

    def criaCartaConvite(self, save=False):
        membros = [
            self.orientador,
            self.coorientador,
            self.externo1,
            self.externo2,
            self.interno1,
            self.interno2,
            self.supl_int,
            self.supl_ext,
        ]
        for membro in membros:
            if membro is None:
                continue

            if save is True:
                self.pdf = PDF()
                self.pdf.alias_nb_pages()
                self.pdf.add_font("Federo", "", os.path.join(_BASE_DIR, "Fonts", "Federo-Regular.ttf"))
                self.pdf.add_font("Verdana", "", os.path.join(_BASE_DIR, "Fonts", "verdana.ttf"))
                self.pdf.add_font("Verdana", "B", os.path.join(_BASE_DIR, "Fonts", "verdanab.ttf"))
                self.pdf.add_font("Verdana", "I", os.path.join(_BASE_DIR, "Fonts", "verdanai.ttf"))
                self.pdf.add_font("calibri", "", os.path.join(_BASE_DIR, "Fonts", "calibri.ttf"))
                self.pdf.add_font("calibri", "B", os.path.join(_BASE_DIR, "Fonts", "calibrib.ttf"))
                self.pdf.add_font("calibri", "I", os.path.join(_BASE_DIR, "Fonts", "calibrii.ttf"))
                self.pdf.add_font("Arial", "", os.path.join(_BASE_DIR, "Fonts", "arial.ttf"))

            self.pdf.add_page()
            self.pdf.set_left_margin(20)
            self.pdf.set_right_margin(20)
            # self.pdf.set_auto_page_break(1, 15)
            self.pdf.set_y(40)

            self.pdf.set_font("calibri", "", 11)
            if self.data_convite is None:
                self.data_convite = date.today()

            lang = membro[-1]
            data = {}
            data["pt"] = (
                f"Porto Alegre, {self.data_convite.day} de {self.dataMesExtenso(self.data_convite.month)} de {self.data_convite.year}"
            )
            data["en"] = (
                f"Porto Alegre, {self.dataMesExtenso_en(self.data_convite.month).capitalize()} {self.ordinalDay(self.data_convite.day)}, {self.data_convite.year}"
            )
            self.pdf.cell(0, 6, data[lang], align="R")
            self.pdf.ln(15)

            saudacao = {}
            saudacao["en"] = "Dear Dr."
            if membro[0] == 0:
                saudacao["pt"] = "Ilmo. Senhor"
            else:
                saudacao["pt"] = "Ilma. Senhora"

            self.pdf.cell(0, 5, saudacao[lang], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
            self.pdf.cell(
                0,
                5,
                f"**{membro[1]}**",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                markdown=True,
            )
            self.pdf.cell(0, 5, f"{membro[3]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
            self.pdf.ln(10)

            paragrafo = {}
            if membro[0] == 0:
                paragrafo["pt"] = "Prezado Senhor:\n\n"
                paragrafo["en"] = "Dear Sir:\n\n"
            else:
                paragrafo["pt"] = "Prezada Senhora:\n\n"
                paragrafo["en"] = "Dear Maddam:\n\n"

            convite = ""
            if membros.index(membro) == 0:
                convite = "compor, na condição de **PRESIDENTE**,"
            elif membros.index(membro) == 1:
                convite = "acompanhar"
            elif membros.index(membro) >= 6:
                convite = "compor, na condição de **SUPLENTE**,"
            else:
                convite = "compor, na condição de membro **TITULAR**,"

            tratamentoAluno = ""
            if self.nome[0] == 0:
                tratamentoAluno = f"do estudante **{self.nome[1]}**"
            else:
                tratamentoAluno = f"da estudante **{self.nome[1]}**"

            paragrafo["pt"] += (
                "É com satisfação que, em nome da Comissão Coordenadora do Programa de Pós-Graduação em Física da Universidade Federal do Rio Grande do Sul, convido Vossa Senhoria para {}  a Banca Avaliadora d{} {} {} intitulada: __“{}”__ __(“{}”)__.\n\nOs membros da banca são:\n".format(
                    convite,
                    "o" if self.tipo == 2 else "a",
                    self.tipoAta(self.tipo),
                    tratamentoAluno,
                    self.titulo,
                    self.titulo2,
                )
            )

            tipo = self.tipoAtaEn(self.tipo)

            paragrafo["en"] += (
                "It is a great pleasure, on behalf of the coordinate comission of the Graduate Program in Physics of the Universidade Federal do Rio Grande do Sul, to invite you to take part in the {} Committee of **{}**, whose title is (__“{}”__)\nThe members of the committee are:\n".format(
                    tipo, self.nome[1], self.titulo2
                )
            )
            self.pdf.multi_cell(0, 6, paragrafo[lang], align="J", markdown=True)

            for membro1 in membros:
                funcao = {}
                if membro1 is None:
                    continue
                elif membros.index(membro1) == 0:
                    if membro1[0] == 0:
                        funcao["pt"] = "Orientador/Presidente - "
                    else:
                        funcao["pt"] = "Orientadora/Presidente - "
                    funcao["en"] = "Advisor/President - "

                elif membros.index(membro1) == 1:
                    if membro1[0] == 0:
                        funcao["pt"] = "Coorientador - "
                    else:
                        funcao["pt"] = "Coorientadora - "
                    funcao["en"] = "Co-advisor - "
                elif membros.index(membro1) == 6:
                    funcao["pt"] = "Suplente Interno - "
                    funcao["en"] = "Internal Substitute - "
                elif membros.index(membro1) == 7:
                    funcao["pt"] = "Suplente Externo - "
                    funcao["en"] = "External Substitute - "
                else:
                    funcao["pt"] = ""
                    funcao["en"] = ""

                s = (" " * 15) + "**• " + membro1[1] + "**"
                width = round(self.pdf.get_string_width(s) + 0.5)

                self.pdf.cell(
                    width,
                    6,
                    s + " (" + funcao[lang] + f"{membro1[2]})",
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                    align="L",
                    markdown=True,
                )

            self.pdf.ln(5)

            data["pt"] = f"Data: **{self.data.day} de {self.dataMesExtenso(self.data.month)} de {self.data.year}**"
            data["en"] = (
                f"Date: **{self.dataMesExtenso_en(self.data.month).capitalize()} {self.ordinalDay(self.data.day)}, {self.data.year}**"
            )
            self.pdf.cell(
                0,
                6,
                data[lang],
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                markdown=True,
            )

            if self.link is not None:
                s = "Link: "
                self.pdf.cell(self.pdf.get_string_width(s), 6, s, align="L", markdown=True)
                self.pdf.set_text_color(0, 0, 255)
                self.pdf.multi_cell(
                    0,
                    6,
                    f"{self.link}",
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                    align="L",
                    markdown=True,
                    wrapmode="CHAR",
                )
                self.pdf.set_text_color(0, 0, 0)

            if self.local_banca is not None:
                self.pdf.multi_cell(
                    0,
                    6,
                    f"Local: {self.local_banca}",
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                    align="L",
                    markdown=True,
                    wrapmode="CHAR",
                )

            hora = {}
            hora["pt"] = f"Horário: **{self.horario.hour}h{self.horario.minute:02d}**"
            hora["en"] = (
                f"Start Time: **{self.horario.hour % 12}:{self.horario.minute:02d} {'PM' if self.horario.hour > 12 else 'AM'}**"
            )
            self.pdf.cell(0, 6, hora[lang], align="L", markdown=True)

            self.pdf.ln(15)

            despedida = {}
            if membros.index(membro) < 6:
                despedida["pt"] = (
                    "Esperando contar com sua participação, apresento a Vossa Senhoria cordiais saudações."
                )
                despedida["en"] = "Hoping to count on your participation, wish you the best."
            else:
                despedida["pt"] = (
                    "Em caso de necessidade, entraremos em contato para solicitar a sua participação.\nApresento a Vossa Senhoria cordiais saudações."
                )
                despedida["en"] = "If needed, we will enter in contact, wish you the best."

            self.pdf.multi_cell(0, 6, despedida[lang], align="L", markdown=True)
            self.pdf.image(
                os.path.join(_BASE_DIR, "assinatura.jpg"),
                x=self.pdf.center(w=80),
                y=self.pdf.get_y() + 10,
                w=60,
                h=30,
            )
            if save is True:
                funcao = None
                if membros.index(membro) == 0:
                    funcao = "ORIENTADOR"
                elif membros.index(membro) == 1:
                    funcao = "COORIENTADOR"
                elif membros.index(membro) >= 6:
                    funcao = "SUPLENTE"
                else:
                    funcao = "TITULAR"
                self.pdf.output(os.path.join(self.dir, "Carta Convite " + funcao + " - " + membro[1] + ".pdf"))

    def criaParecer(self, save=False):
        banca = [self.externo1, self.externo2, self.interno1, self.interno2]

        for membro in banca:
            if membro is None:
                continue

            if save is True:
                self.pdf = PDF()
                self.pdf.alias_nb_pages()
                self.pdf.add_font("Federo", "", os.path.join(_BASE_DIR, "Fonts", "Federo-Regular.ttf"))
                self.pdf.add_font("Verdana", "", os.path.join(_BASE_DIR, "Fonts", "verdana.ttf"))
                self.pdf.add_font("Verdana", "B", os.path.join(_BASE_DIR, "Fonts", "verdanab.ttf"))
                self.pdf.add_font("Verdana", "I", os.path.join(_BASE_DIR, "Fonts", "verdanai.ttf"))
                self.pdf.add_font("calibri", "", os.path.join(_BASE_DIR, "Fonts", "calibri.ttf"))
                self.pdf.add_font("calibri", "B", os.path.join(_BASE_DIR, "Fonts", "calibrib.ttf"))
                self.pdf.add_font("calibri", "I", os.path.join(_BASE_DIR, "Fonts", "calibrii.ttf"))

            self.pdf.add_page()
            self.pdf.set_left_margin(20)
            self.pdf.set_right_margin(20)
            # self.pdf.set_auto_page_break(1, 15)
            self.pdf.set_y(40)

            lang = membro[-1]
            data = {}
            data["pt"] = f"Porto Alegre, {self.data.day} de {self.dataMesExtenso(self.data.month)} de {self.data.year}"
            data["en"] = (
                f"Porto Alegre, {self.dataMesExtenso_en(self.data.month).capitalize()} {self.ordinalDay(self.data.day)}, {self.data.year}"
            )
            self.pdf.set_font("calibri", "", 11)
            self.pdf.cell(0, 6, data[lang], align="R")
            self.pdf.ln(25)

            titulo = {}
            titulo["pt"] = self.tipoAta(self.tipo)
            titulo["en"] = self.tipoAtaEn(self.tipo)

            self.pdf.set_font("Verdana", "", 16)
            self.pdf.cell(0, 6, f"**{titulo[lang]}**", align="C", markdown=True)
            self.pdf.ln(20)
            alt = self.pdf.get_y()
            self.pdf.line(20, alt, 190, alt)
            self.pdf.ln(10)

            self.pdf.set_font("calibri", "", 14)
            paragrafo = {}
            paragrafo["pt"] = f"Autor: **{self.nome[1]}**\n\n"
            paragrafo["en"] = f"Author: **{self.nome[1]}**\n\n"
            self.pdf.multi_cell(
                0,
                6,
                paragrafo[lang] + f"Título: __{self.titulo}__\n\n" + f"Title: __{self.titulo2}__",
                0,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                markdown=True,
            )
            self.pdf.ln(10)
            alt = self.pdf.get_y()
            self.pdf.line(20, alt, 190, alt)

            paragrafo["pt"] = "Declaro que examinei o trabalho acima, considerando-o:"
            paragrafo["en"] = "I declare that I have examined the work above, considering it:"
            self.pdf.ln(10)
            self.pdf.cell(
                0,
                6,
                paragrafo[lang],
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                markdown=True,
            )
            self.pdf.ln(10)

            opcoes = {}
            if self.tipo == 2:
                opcoes["pt"] = "\u20dd Aprovado sem restrições\n\u20dd Aprovado com restrições\n\u20dd Não aprovado\n"
                opcoes["en"] = (
                    "\u20dd Aproved without restrictions\n\u20dd Aproved with restrictions\n\u20dd Not aproved\n"
                )
            else:
                opcoes["pt"] = "Aprovado\nReprovado\n"
                opcoes["en"] = "Aproved \nReproved \n"

                rect = 6
                width = self.pdf.get_string_width(opcoes[lang].split("\n")[0])
                padding = 105 - (width // 2 + rect) - 2
                self.pdf.set_x(padding)
                self.pdf.cell(rect, rect, "", 1)
                self.pdf.cell(
                    width,
                    6,
                    opcoes[lang].split("\n")[0],
                    align="L",
                    markdown=True,
                    center=True,
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                )

                self.pdf.ln(2)
                self.pdf.set_x(padding)
                self.pdf.cell(rect, rect, "", 1)
                self.pdf.cell(
                    width,
                    6,
                    opcoes[lang].split("\n")[1],
                    align="L",
                    markdown=True,
                    center=True,
                )

                self.pdf.ln(40)
                alt = self.pdf.get_y()
                width = self.pdf.get_string_width(membro[1])
                x = (210 - width) / 2
                self.pdf.line(x, alt, x + width, alt)
                self.pdf.cell(
                    None,
                    6,
                    "**" + membro[1] + "**",
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                    align="C",
                    markdown=True,
                    center=True,
                )
                self.pdf.cell(None, 6, membro[3], align="C", markdown=True, center=True)

            if save is True:
                self.pdf.output(os.path.join(self.dir, "Parecer - " + membro[1] + ".pdf"))

    def criaCartaz(self, save=False):
        if save is True:
            self.pdf = PDF()
            self.pdf.alias_nb_pages()
            self.pdf.add_font("Federo", "", os.path.join(_BASE_DIR, "Fonts", "Federo-Regular.ttf"))
            self.pdf.add_font("Verdana", "", os.path.join(_BASE_DIR, "Fonts", "verdana.ttf"))
            self.pdf.add_font("Verdana", "B", os.path.join(_BASE_DIR, "Fonts", "verdanab.ttf"))
            self.pdf.add_font("Verdana", "I", os.path.join(_BASE_DIR, "Fonts", "verdanai.ttf"))
            self.pdf.add_font("calibri", "", os.path.join(_BASE_DIR, "Fonts", "calibri.ttf"))
            self.pdf.add_font("calibri", "B", os.path.join(_BASE_DIR, "Fonts", "calibrib.ttf"))
            self.pdf.add_font("calibri", "I", os.path.join(_BASE_DIR, "Fonts", "calibrii.ttf"))
        self.pdf.add_page(orientation="L")
        self.pdf.set_auto_page_break(False)
        margin = 25
        self.pdf.set_left_margin(margin)
        self.pdf.set_right_margin(margin)
        self.pdf.add_font("ArialBLK", "", os.path.join(_BASE_DIR, "Fonts", "ARIBLK.TTF"))
        self.pdf.set_font("ArialBLK", "", 24)
        self.pdf.ln(35)
        self.pdf.cell(0, None, self.tipoAta(self.tipo).upper(), align="C")
        self.pdf.ln(15)
        self.pdf.set_font("Calibri", "", 24)
        self.pdf.cell(
            0,
            None,
            f"AUTOR: **{self.nome[1]}**",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            markdown=1,
        )
        self.pdf.ln(10)
        self.pdf.set_font("Verdana", "", 18)
        self.pdf.multi_cell(
            0,
            None,
            f"TITULO: **“{self.titulo}”**",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            markdown=1,
            wrapmode="WORD",
        )
        self.pdf.ln(5)
        self.pdf.multi_cell(
            0,
            None,
            f"TITLE: **“{self.titulo2}”**",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            markdown=1,
            wrapmode="WORD",
        )
        self.pdf.ln(15)
        self.pdf.set_font("Calibri", "", 14)
        self.pdf.cell(
            0,
            None,
            "Orientador:" + " " * 12 + f"**{self.orientador[1]}**",
            align="l",
            markdown=1,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        if self.coorientador is not None:
            self.pdf.cell(
                0,
                None,
                "Coorientador:" + " " * 8 + f"**{self.coorientador[1]}**",
                align="l",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                markdown=1,
            )
        self.pdf.ln(8)
        self.pdf.cell(
            0,
            None,
            "Banca Examinadora:",
            align="L",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            markdown=1,
        )
        self.pdf.ln(5)
        membros = [self.externo1, self.externo2, self.interno1, self.interno2]

        for membro in membros:
            if membro is None:
                continue

            s = (" " * 30) + "**• " + membro[1] + "**" + f" ({membro[2]})"
            width = round(self.pdf.get_string_width(s) + 0.5)
            self.pdf.cell(
                width,
                None,
                s,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                markdown=True,
            )

        self.pdf.set_y(-30)
        self.pdf.line(
            margin,
            self.pdf.get_y(),
            self.pdf.get_page_width() - margin,
            self.pdf.get_y(),
        )
        self.pdf.ln(5)
        self.pdf.cell(
            0,
            None,
            f"Data: **{self.data.day} de {self.dataMesExtenso(self.data.month)} de {self.data.year}**\n",
            align="L",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        if self.local_banca is not None:
            self.pdf.cell(
                0,
                None,
                f"Local: **{self.local_banca}**\n",
                align="L",
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
        if self.link is not None:
            self.pdf.cell(
                0,
                None,
                f"Link: **{self.link}**\n",
                align="L",
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(self.link)
            qr.make(fit=True)
            _qr_path = os.path.join(_BASE_DIR, "qrcode.png")
            qr.make_image().save(_qr_path)
            self.pdf.image(
                _qr_path,
                x=self.pdf.get_page_width() - 2 * margin,
                y=210 - 28,
                w=25,
                h=25,
            )
        self.pdf.cell(
            0,
            None,
            f"Horário: **{self.horario.hour}h{self.horario.minute:02d}**",
            align="L",
            markdown=True,
        )
        if save is True:
            self.pdf.output(os.path.join(self.dir, "Cartaz - " + self.nome[1] + ".pdf"))

    def criaRelatoriaAvaliacao(self, save=False):
        if save is True:
            self.pdf = PDF()
            self.pdf.alias_nb_pages()
            self.pdf.add_font("Federo", "", os.path.join(_BASE_DIR, "Fonts", "Federo-Regular.ttf"))
            self.pdf.add_font("Verdana", "", os.path.join(_BASE_DIR, "Fonts", "verdana.ttf"))
            self.pdf.add_font("Verdana", "B", os.path.join(_BASE_DIR, "Fonts", "verdanab.ttf"))
            self.pdf.add_font("Verdana", "I", os.path.join(_BASE_DIR, "Fonts", "verdanai.ttf"))
            self.pdf.add_font("calibri", "", os.path.join(_BASE_DIR, "Fonts", "calibri.ttf"))
            self.pdf.add_font("calibri", "B", os.path.join(_BASE_DIR, "Fonts", "calibrib.ttf"))
            self.pdf.add_font("calibri", "I", os.path.join(_BASE_DIR, "Fonts", "calibrii.ttf"))
        # Primeira Página do Relatório
        self.pdf.add_page()
        margin = 20
        self.pdf.set_left_margin(margin)
        self.pdf.set_right_margin(margin)

        self.pdf.ln(30)
        self.pdf.set_font("Calibri", "", 16)
        self.pdf.multi_cell(
            0,
            None,
            "**RELATÓRIO DE AVALIAÇÃO\nDO EXAME DE QUALIFICAÇÃO AO DOUTORADO**",
            align="C",
            markdown=True,
        )
        self.pdf.ln(10)

        self.pdf.line(margin, self.pdf.get_y(), 210 - margin, self.pdf.get_y())
        self.pdf.ln(10)

        self.pdf.set_font("Verdana", "", 12)
        self.pdf.multi_cell(
            0,
            None,
            f"Autor: **{self.nome[1]}**\n\nTítulo: “{self.titulo}”\n\n__Title: “{self.titulo2}”__",
            align="L",
            markdown=True,
            wrapmode="WORD",
            new_y="NEXT",
        )
        self.pdf.ln(10)
        self.pdf.line(margin, self.pdf.get_y(), 210 - margin, self.pdf.get_y())

        self.pdf.set_font("calibri", "", 10)
        self.pdf.cell(
            0,
            10,
            f"Orientador: **{self.orientador[1]}**",
            align="L",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.pdf.line(margin, self.pdf.get_y(), 210 - margin, self.pdf.get_y())

        self.pdf.cell(
            0,
            10,
            "**ORIENTAÇÕES À BANCA:**",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.pdf.multi_cell(
            0,
            None,
            "**1** - Todas as páginas desse relatório devem ser RUBRICADAS pelos membros da banca, que também devem FIRMAR SUAS ASSINATURAS na última página.",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.pdf.ln(2)
        self.pdf.multi_cell(
            0,
            None,
            "**2** – O preenchimento dos quadros de avaliação deve corresponder ao NÚMERO DE MEMBROS DA BANCA que consideram o trabalho **MB** = Muito Bom; **B** = Bom; **R** = Regular; **I** = Insuficiente em cada quesito avaliado.",
            markdown=True,
        )
        self.pdf.ln(5)
        rect_top = self.pdf.get_y()
        rect_height = 297 - rect_top - 17
        self.pdf.rect(margin, rect_top, 210 - 2 * margin, rect_height)

        table_data = (
            ("MB", "B", "R", "I"),
            (" ", " ", " ", " "),
            (" ", " ", " ", " "),
            (" ", " ", " ", " "),
            (" ", " ", " ", " "),
            (" ", " ", " ", " "),
        )
        size = 10
        height = size * 0.7
        with self.pdf.table(
            width=4 * size,
            col_widths=(size, size, size, size),
            align="R",
            line_height=height,
            text_align="CENTER",
        ) as table:
            for data_row in table_data:
                table.row(data_row)

        self.pdf.set_y(rect_top)
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "**Avaliação do Aluno:**",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Qualidade do texto escrito?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Qualidade da apresentação oral?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Conhecimento da literatura atualizada relacionada ao tema?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Domínio da metodologia pertinente?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Segurança, maturidade e nível de conhecimento?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )

        self.pdf.ln(25)
        self.pdf.cell(
            0,
            None,
            "**Sugestões e/ou comentários (opcional):**",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="L",
        )
        rect_bottom = rect_top + rect_height
        empty_lines = 7
        dh = 8
        self.pdf.set_y(rect_bottom - empty_lines * dh)
        for i in range(empty_lines - 1):
            self.pdf.cell(
                0,
                dh,
                "",
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                border=1,
            )

        # Segunda página do Relatório
        self.pdf.add_page()
        margin = 20
        self.pdf.set_left_margin(margin)
        self.pdf.set_right_margin(margin)

        space_between = 4
        self.pdf.ln(space_between)
        rect_top = self.pdf.get_y()
        rect_height = (self.pdf.eph - 3 * space_between) // 2
        rect_bottom = rect_top + rect_height
        self.pdf.rect(margin, rect_top, 210 - 2 * margin, rect_height)

        table_data = (
            ("MB", "B", "R", "I"),
            (" ", " ", " ", " "),
            (" ", " ", " ", " "),
            (" ", " ", " ", " "),
        )
        size = 10
        height = size * 0.7
        with self.pdf.table(
            width=4 * size,
            col_widths=(size, size, size, size),
            align="R",
            line_height=height,
            text_align="CENTER",
        ) as table:
            for data_row in table_data:
                table.row(data_row)

        self.pdf.set_y(rect_top)
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "**Avaliação do desenvolvimento do projeto:**",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Estágio de desenvolvimento atual do trabalho face aos objetivos propostos",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Perspectiva da publicação em periódicos indexados de circulação internacional?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.cell(
            210 - 2 * 20 - 4 * size,
            height,
            "Adequação do cronograma apresentado para finalização do trabalho?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.ln(4)

        table_data = (
            ("SIM", "NÃO"),
            (" ", " "),
            (" ", " "),
        )
        size = 20
        height = size * 0.35
        cur_y = self.pdf.get_y()
        with self.pdf.table(
            width=2 * size,
            col_widths=(size, size),
            align="R",
            line_height=height,
            text_align="CENTER",
        ) as table:
            for data_row in table_data:
                table.row(data_row)

        self.pdf.set_y(cur_y)
        self.pdf.cell(
            210 - 2 * 20 - 2 * size,
            height,
            "",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.pdf.cell(
            210 - 2 * 20 - 2 * size,
            height,
            "Foi verificada a existência de algum impasse evidente no desenvolvimento da tese?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )
        self.pdf.cell(
            210 - 2 * 20 - 2 * size,
            height,
            "Já existem publicações? Em caso positivo, quantas?",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="R",
        )

        self.pdf.ln(7)
        self.pdf.cell(
            0,
            None,
            "Sugestões e/ou comentários (opcional), ou especificação no caso de verificação de algum impasse:",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="L",
        )
        rect_bottom = rect_top + rect_height
        empty_lines = 7
        dh = 8
        self.pdf.set_y(rect_bottom - empty_lines * dh)
        for i in range(empty_lines - 1):
            self.pdf.cell(
                0,
                dh,
                "",
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                border=1,
            )

        self.pdf.set_y(rect_bottom + space_between)
        rect_top = self.pdf.get_y()
        self.pdf.rect(margin, rect_top, 210 - 2 * margin, rect_height)
        self.pdf.cell(
            0,
            height,
            "**Avaliação final**(MARCAR OPÇÃO)",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.pdf.ln(5)
        self.pdf.cell(
            (210 - 2 * 20 - 10) / 2,
            height,
            "**Aprovado SEM restrições**",
            markdown=True,
            align="R",
        )
        self.pdf.cell(
            10,
            height,
            "",
            border=True,
            center=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

        self.pdf.cell(
            (210 - 2 * 20 - 10) / 2,
            height,
            "**Aprovado COM restrições**",
            markdown=True,
            align="R",
        )
        self.pdf.cell(10, height, "", border=True, center=True)
        self.pdf.cell(
            (210 - 2 * 20 - 10) / 2,
            height,
            "(Preencher quadro abaixo)",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="L",
        )

        self.pdf.cell(
            (210 - 2 * 20 - 10) / 2,
            height,
            "**Não aprovado**",
            markdown=True,
            align="R",
        )
        self.pdf.cell(10, height, "", border=True, center=True)
        self.pdf.cell(
            (210 - 2 * 20 - 10) / 2,
            height,
            "(Preencher quadro abaixo)",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="L",
        )

        self.pdf.ln(23)
        self.pdf.multi_cell(
            0,
            None,
            "**Recomendaçẽos e comentários\n(preenchimento opcional no caso de aprovação** __sem restrições__**; obrigatório nos demais casos)**",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="L",
        )
        rect_bottom = rect_top + rect_height
        self.pdf.set_y(rect_bottom - empty_lines * dh)
        for i in range(empty_lines - 1):
            self.pdf.cell(
                0,
                dh,
                "",
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
                border=True,
            )

        # Terceira página do Relatório
        self.pdf.add_page()
        margin = 20
        self.pdf.set_left_margin(margin)
        self.pdf.set_right_margin(margin)
        self.pdf.ln(10)

        self.pdf.set_font("Calibri", "", 12)
        self.pdf.multi_cell(
            0,
            height,
            f"Os abaixo assinados certificam que a avaliação em pauta foi realizada na data de **{self.data.day} de {self.dataMesExtenso(self.data.month)} de {self.data.year}**",
            markdown=True,
            align="J",
        )

        self.pdf.ln(10)
        membros = [self.externo1, self.interno1, self.interno2]
        for membro in membros:
            height = 12
            x, y = self.pdf.get_x(), self.pdf.get_y()
            self.pdf.line(x + 30, y, x + 30, y + height * 3)
            self.pdf.multi_cell(
                30,
                height,
                " ".join(("**", *membro[1].split(" ")[:2], "**")),
                markdown=True,
                new_y=YPos.LAST,
                align="R",
            )
            self.pdf.multi_cell(
                210 - 2 * margin - 30,
                height,
                " ".join(("**", *membro[1].split(" ")[2:], "**")),
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
            )
            self.pdf.multi_cell(30, height, "Instituição:", markdown=True, new_y=YPos.LAST, align="R")
            self.pdf.multi_cell(
                210 - 2 * margin - 30,
                height,
                membro[3],
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
            )

            self.pdf.multi_cell(30, height, "Assinatura:", markdown=True, new_y=YPos.LAST, align="R")
            self.pdf.multi_cell(
                210 - 2 * margin - 30,
                height,
                "",
                markdown=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align="L",
            )

            x, y = self.pdf.get_x(), self.pdf.get_y()
            self.pdf.line(x + 30, y, 210 - margin, y)

            self.pdf.ln(10)

        self.pdf.ln(5)
        x, y = self.pdf.get_x(), self.pdf.get_y()
        self.pdf.rect(x, y, 210 - 2 * margin, 70, "D")

        self.pdf.ln(3)
        self.pdf.multi_cell(
            0,
            8,
            "Declaramos ter tomado ciência desse relatório de avaliação e caso existam providências a serem tomadas, as executaremos conforme acima informado. Assinam:",
            markdown=True,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="L",
        )
        height = 15
        self.pdf.ln(5)
        self.pdf.multi_cell(50, height, "Orientador:", markdown=True, new_y=YPos.LAST, align="R")
        x, y = self.pdf.get_x(), self.pdf.get_y()
        self.pdf.line(x, y + height / 2 + 2, x + 70, y + height / 2 + 2)
        self.pdf.ln()

        self.pdf.multi_cell(50, height, "Aluno:", markdown=True, new_y=YPos.LAST, align="R")
        x, y = self.pdf.get_x(), self.pdf.get_y()
        self.pdf.line(x, y + height / 2 + 2, x + 70, y + height / 2 + 2)
        self.pdf.ln(15)
        self.pdf.cell(
            0,
            height,
            f"Porto Alegre, {self.data.day} de {self.dataMesExtenso(self.data.month)} de {self.data.year}.",
            align="R",
        )

        if save is True:
            self.pdf.output(os.path.join(self.dir, "Relatório de Avaliação - " + self.nome[1] + ".pdf"))


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        # content
        c = f.readlines()

    c = list(map(lambda s: s.replace("\n", ""), c))
    c = list(map(lambda s: None if s == "None" else s, c))

    d = datetime.strptime(c[2], "%Y-%m-%d %H-%M")
    i = datetime.strptime(c[3], "%Y-%m-%d")  # invite
    banca = Banca(
        nome=eval(c[0]),
        tipo=int(c[1]),  # 1 - Mestrado, 2 - Exame qualificação, 3 - Doutorado
        data=date(d.year, d.month, d.day),
        # TODO: acoplar data e horario (não há razão pra estarem separados)
        horario=time(d.hour, d.minute),
        data_convite=date(i.year, i.month, i.day),
        ata=int(c[4]),
        local_banca=c[5],
        link=c[6],
        orientador=eval(c[7]),
        coorientador=eval(c[8]) if c[8] is not None else None,
        externo1=eval(c[9]),
        externo2=eval(c[10]) if c[10] is not None else None,
        interno1=eval(c[11]),
        interno2=eval(c[12]),
        supl_int=eval(c[13]) if c[13] is not None else None,
        supl_ext=eval(c[14]) if c[14] is not None else None,
        titulo=eval(c[15]),
        titulo2=eval(c[16]),
    )

    # banca.criaAta(save=True)
    banca.criaCartaConvite(save=True)
    # banca.criaParecer(save=True)
    banca.criaCartaz(save=True)
    banca.criaRelatoriaAvaliacao(save=True)
