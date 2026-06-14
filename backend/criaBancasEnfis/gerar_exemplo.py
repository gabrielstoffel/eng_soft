"""Gera cartas-convite de exemplo do ppgenfis para inspeção visual.

Uso:
    cd backend && uv run python criaBancasEnfis/gerar_exemplo.py

Escreve um PDF por membro em `criaBancasEnfis/exemplo/`, cobrindo todos os
papéis (orientador/presidente, coorientador, titulares e suplente).
"""

import os
import shutil
from datetime import date, time

from criaBancasEnfis import Banca

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exemplo")

# tupla de membro: (genero, nome, instituicao, cidade, idioma)
#   genero: 0 = Prof. Dr.   1 = Profa. Dra.
banca = Banca(
    nome=(1, "Joana Reis"),
    tipo=1,  # 1=Mestrado, 2=Qualificação, 3=Doutorado
    horario=time(14, 30),
    data=date(2026, 8, 20),
    data_convite=date(2026, 6, 12),
    ata=200,
    local_banca="Sala 204 do Instituto de Física - UFRGS",
    link="https://meet.example/banca-200",
    orientador=(0, "Carlos Pereira", "UFRGS", "Porto Alegre, RS", "pt"),
    coorientador=(1, "Marta Dias", "UFRGS", "Porto Alegre, RS", "pt"),
    externo1=(1, "Maria Souza", "USP", "São Paulo, SP", "pt"),
    externo2=None,
    interno1=(0, "Pedro Lima", "UFRGS", "Porto Alegre, RS", "pt"),
    interno2=(1, "Ana Costa", "UFRGS", "Porto Alegre, RS", "pt"),
    supl_int=(0, "Bruno Alves", "UFRGS", "Porto Alegre, RS", "pt"),
    supl_ext=None,
    titulo="O ensino de mecânica quântica no ensino médio",
    titulo2=None,
    data_parecer=date(2026, 8, 25),
)

banca.criaCartaConvite(save=True)
banca.criaParecer(save=True)
banca.criaCartaz(save=True)

# A Banca escreve em criaBancasEnfis/Bancas/<ata> - <nome>/. Copia para ./exemplo/
# para facilitar a inspeção.
os.makedirs(_OUT, exist_ok=True)
for f in os.listdir(_OUT):
    os.remove(os.path.join(_OUT, f))
for f in sorted(os.listdir(banca.dir)):
    shutil.copy(os.path.join(banca.dir, f), os.path.join(_OUT, f))
shutil.rmtree(os.path.join(os.path.dirname(_OUT), "Bancas"), ignore_errors=True)

print(f"PDFs gerados em: {_OUT}")
for f in sorted(os.listdir(_OUT)):
    print("  ", f)
