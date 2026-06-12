"""Attachment persistence: PDFs uploaded with a banca petition.

Files are stored in GridFS, with one metadata document per attachment in the
`attachments` collection (bound to the banca by its decision token). Kept as
module-level functions to match the other I/O services (email_service,
document_service).
"""

from dataclasses import dataclass
from datetime import datetime, timezone

import gridfs

from app.infrastructure.database import get_db
from app.logger import get_logger

logger = get_logger(__name__)

# Accepted attachment kinds. Positional `roles` may bind a lattes_cv to its
# external member; the other kinds ignore it.
ATTACHMENT_KINDS = ("lattes_cv", "texto", "press_release", "artigo")


@dataclass
class AttachmentUpload:
    """An in-memory attachment ready to be persisted and/or emailed."""
    filename: str
    content: bytes
    content_type: str
    kind: str
    member_role: str | None = None


def store_attachments(token: str, attachments: list[AttachmentUpload]) -> list[dict]:
    """Persist attachments to GridFS + the `attachments` collection.

    Returns the saved metadata (kind/member_role/filename) for each file.
    """
    if not attachments:
        return []

    db = get_db()
    fs = gridfs.GridFS(db)
    saved: list[dict] = []
    for a in attachments:
        file_id = fs.put(a.content, filename=a.filename, content_type=a.content_type)
        db["attachments"].insert_one({
            "decision_token": token,
            "kind": a.kind,
            "member_role": a.member_role,
            "filename": a.filename,
            "gridfs_id": file_id,
            "uploaded_at": datetime.now(timezone.utc),
        })
        saved.append({"kind": a.kind, "member_role": a.member_role, "filename": a.filename})

    logger.info("store_attachments.end", {"token": token, "count": len(saved)})
    return saved


def load_attachments(token: str, kind: str | None = None) -> list[tuple[str, bytes, str]]:
    """Load stored attachments as (filename, content, content_type) tuples.

    Optionally filter by kind (e.g. "texto" for the thesis/dissertation PDF).
    """
    db = get_db()
    fs = gridfs.GridFS(db)
    query: dict = {"decision_token": token}
    if kind is not None:
        query["kind"] = kind

    out: list[tuple[str, bytes, str]] = []
    for doc in db["attachments"].find(query):
        try:
            grid = fs.get(doc["gridfs_id"])
            content = grid.read()
        except Exception as e:
            logger.error("load_attachments.read_error", {"token": token, "message": str(e)})
            continue
        content_type = getattr(grid, "content_type", None) or "application/pdf"
        out.append((doc.get("filename", "anexo.pdf"), content, content_type))
    return out
