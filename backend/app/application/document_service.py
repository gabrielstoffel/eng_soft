import contextlib
import io
import os
import shutil
import sys
import tempfile
import traceback
import zipfile

from app.domain.errors import DocumentGenerationError
from app.domain.models import BancaRequest, FileManifestEntry, MemberInfo, MemberRole
from app.logger import get_logger
from app.result import Err, Ok, Result

logger = get_logger(__name__)

_CRIABANCAS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "criaBancas")
sys.path.insert(0, os.path.abspath(_CRIABANCAS_DIR))

from criaBancas import Banca  # noqa: E402

# Mirrors the role index → "FUNCAO" mapping inside criaBancas.criaCartaConvite.
_CONVITE_FUNCAO: dict[MemberRole, str] = {
    "orientador": "ORIENTADOR",
    "coorientador": "COORIENTADOR",
    "externo1": "TITULAR",
    "externo2": "TITULAR",
    "interno1": "TITULAR",
    "interno2": "TITULAR",
    "supl_int": "SUPLENTE",
    "supl_ext": "SUPLENTE",
}

_PARECER_ROLES: tuple[MemberRole, ...] = ("externo1", "externo2", "interno1", "interno2")


def _member_tuple(member: MemberInfo | None) -> tuple | None:
    """Build the (gender, name, institution, ...) tuple criaBancas expects.

    When the member participates remotely, annotate the institution field so the
    information surfaces in the generated documents (ata, carta-convite, cartaz)
    without having to alter the PDF generator itself.
    """
    if member is None:
        return None
    base = list(member.to_tuple())
    if member.remoto and len(base) > 2:
        base[2] = f"{base[2]} (participação remota)"
    return tuple(base)


@contextlib.contextmanager
def _build_banca(req: BancaRequest, ata: int):
    tmp_dir = tempfile.mkdtemp(prefix="sigbah_banca_")
    banca = Banca(
        nome=req.nome.to_tuple(),
        tipo=req.tipo,
        data=req.data,
        horario=req.horario,
        data_convite=None,  # campo removido do modelo; criaBancas usa `data` como fallback
        ata=ata,
        local_banca=req.sala_preferencia,  # substitui o antigo local_banca
        link=req.link,
        orientador=_member_tuple(req.orientador),
        coorientador=_member_tuple(req.coorientador),
        externo1=_member_tuple(req.externo1),
        externo2=_member_tuple(req.externo2),
        interno1=_member_tuple(req.interno1),
        interno2=_member_tuple(req.interno2),
        supl_int=_member_tuple(req.supl_int),
        supl_ext=_member_tuple(req.supl_ext),
        titulo=req.titulo,
        titulo2=req.titulo2,
    )
    original_dir = banca.dir
    banca.dir = tmp_dir
    try:
        with contextlib.suppress(OSError):
            os.rmdir(original_dir)
        yield banca
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _zip_dir(directory: str) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(directory):
            for fname in files:
                full_path = os.path.join(root, fname)
                zf.write(full_path, arcname=os.path.relpath(full_path, directory))
    buf.seek(0)
    return buf


def _generate_all(banca: Banca) -> None:
    banca.criaAta(save=True)
    banca.criaCartaConvite(save=True)
    banca.criaParecer(save=True)
    banca.criaCartaz(save=True)
    if banca.tipo == 2:
        banca.criaRelatoriaAvaliacao(save=True)


def _zip_filename(req: BancaRequest, ata: int) -> str:
    return f"banca_{ata}_{req.nome.name.replace(' ', '_')}.zip"


def _member_prefix(gender: int) -> str:
    return "Profª. Drª. " if gender == 1 else "Prof. Dr. "


def file_manifest(req: BancaRequest) -> list[FileManifestEntry]:
    """Return the list of individual PDFs that would be produced for this banca.

    Filenames mirror those written by `criaBancas.Banca.cria*` methods.
    """
    items: list[FileManifestEntry] = []
    student = req.nome.name

    if req.tipo != 2:
        items.append(
            FileManifestEntry(
                id="ata",
                label=f"Ata - {student}.pdf",
                kind="ata",
                member_role=None,
            )
        )

    items.append(
        FileManifestEntry(
            id="cartaz",
            label=f"Cartaz - {student}.pdf",
            kind="cartaz",
            member_role=None,
        )
    )

    if req.tipo == 2:
        items.append(
            FileManifestEntry(
                id="relatoria_avaliacao",
                label=f"Relatório de Avaliação - {student}.pdf",
                kind="relatoria_avaliacao",
                member_role=None,
            )
        )

    for role, funcao in _CONVITE_FUNCAO.items():
        member = getattr(req, role)
        if member is None:
            continue
        full = f"{_member_prefix(member.gender)}{member.name}"
        items.append(
            FileManifestEntry(
                id=f"carta_convite:{role}",
                label=f"Carta Convite {funcao} - {full}.pdf",
                kind="carta_convite",
                member_role=role,
            )
        )

    for role in _PARECER_ROLES:
        member = getattr(req, role)
        if member is None:
            continue
        full = f"{_member_prefix(member.gender)}{member.name}"
        items.append(
            FileManifestEntry(
                id=f"parecer:{role}",
                label=f"Parecer - {full}.pdf",
                kind="parecer",
                member_role=role,
            )
        )

    return items


def generate_documents(req: BancaRequest, ata: int) -> Result[tuple[io.BytesIO, str], DocumentGenerationError]:
    logger.info("generate_documents.start", {"ata": ata, "tipo": req.tipo})
    try:
        with _build_banca(req, ata) as banca:
            _generate_all(banca)
            buf = _zip_dir(banca.dir)
            zip_name = _zip_filename(req, ata)
            logger.info("generate_documents.end", {"zip": zip_name})
            return Ok((buf, zip_name))
    except Exception as e:
        logger.error("generate_documents.error", {"message": str(e), "traceback": traceback.format_exc()})
        return Err(DocumentGenerationError(message=str(e)))


def generate_files(
    req: BancaRequest, ids: list[str], ata: int
) -> Result[tuple[io.BytesIO, str, str], DocumentGenerationError]:
    """Generate the PDFs identified by `ids`. Returns single PDF if one id, zip otherwise.

    Each id is a manifest entry id (e.g. `ata`, `cartaz`, `carta_convite:orientador`).
    """
    logger.info("generate_files.start", {"ata": ata, "tipo": req.tipo, "ids": ids})

    if not ids:
        return Err(DocumentGenerationError(message="No files selected."))

    manifest = {entry.id: entry for entry in file_manifest(req)}
    requested: list[FileManifestEntry] = []
    for item_id in ids:
        entry = manifest.get(item_id)
        if entry is None:
            return Err(DocumentGenerationError(message=f"Unknown file id: {item_id}"))
        requested.append(entry)

    needed_kinds = {entry.kind for entry in requested}

    try:
        with _build_banca(req, ata) as banca:
            if "ata" in needed_kinds:
                banca.criaAta(save=True)
            if "cartaz" in needed_kinds:
                banca.criaCartaz(save=True)
            if "relatoria_avaliacao" in needed_kinds:
                banca.criaRelatoriaAvaliacao(save=True)
            if "carta_convite" in needed_kinds:
                banca.criaCartaConvite(save=True)
            if "parecer" in needed_kinds:
                banca.criaParecer(save=True)

            picked: list[tuple[str, str]] = []
            for entry in requested:
                path = os.path.join(banca.dir, entry.label)
                if not os.path.exists(path):
                    return Err(DocumentGenerationError(message=f"Generated file missing on disk: {entry.label}"))
                picked.append((entry.label, path))

            if len(picked) == 1:
                label, path = picked[0]
                with open(path, "rb") as f:
                    return Ok((io.BytesIO(f.read()), label, "application/pdf"))

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for label, path in picked:
                    zf.write(path, arcname=label)
            buf.seek(0)
            return Ok((buf, _zip_filename(req, ata), "application/zip"))
    except Exception as e:
        logger.error(
            "generate_files.error",
            {"ids": ids, "message": str(e), "traceback": traceback.format_exc()},
        )
        return Err(DocumentGenerationError(message=str(e)))
