import io
import logging
import os
import sys
import traceback
import zipfile

from app.models import BancaRequest
from app.result import Err, Ok, Result

logger = logging.getLogger(__name__)

_CRIABANCAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "criaBancas")
sys.path.insert(0, os.path.abspath(_CRIABANCAS_DIR))

from criaBancas import Banca  # noqa: E402


def generate_documents(req: BancaRequest) -> Result[tuple[io.BytesIO, str], str]:
    try:
        banca = Banca(
            nome=req.nome.to_tuple(),
            tipo=req.tipo,
            data=req.data,
            horario=req.horario,
            data_convite=req.data_convite,
            ata=req.ata,
            local_banca=req.local_banca,
            link=req.link,
            orientador=req.orientador.to_tuple(),
            coorientador=req.coorientador.to_tuple() if req.coorientador else None,
            externo1=req.externo1.to_tuple(),
            externo2=req.externo2.to_tuple() if req.externo2 else None,
            interno1=req.interno1.to_tuple(),
            interno2=req.interno2.to_tuple(),
            supl_int=req.supl_int.to_tuple() if req.supl_int else None,
            supl_ext=req.supl_ext.to_tuple() if req.supl_ext else None,
            titulo=req.titulo,
            titulo2=req.titulo2,
        )

        banca.criaAta(save=True)  # has internal guard: skips for tipo==2
        banca.criaCartaConvite(save=True)
        banca.criaParecer(save=True)
        banca.criaCartaz(save=True)
        if req.tipo == 2:
            banca.criaRelatoriaAvaliacao(save=True)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(banca.dir):
                for fname in files:
                    full_path = os.path.join(root, fname)
                    zf.write(full_path, arcname=os.path.relpath(full_path, banca.dir))
        buf.seek(0)

        zip_name = f"banca_{banca.ata}_{banca.nome[1].replace(' ', '_')}.zip"
        return Ok((buf, zip_name))
    except Exception as e:
        logger.error(traceback.format_exc())
        return Err(str(e))
