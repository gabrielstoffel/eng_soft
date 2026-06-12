import { IconUpload, IconX } from "@tabler/icons-react";
import { useCallback, useRef, useState } from "react";
import { useFormContext } from "react-hook-form";
import type { NewBancaFormState } from "../../../types/new-banca.ts";

type Props = { disabled?: boolean };
type FileEntry = { file: File; kind: string; id: string };

let fileIdCounter = 0;

export default function BancaAttachmentsSection({ disabled = false }: Props) {
  const { watch } = useFormContext<NewBancaFormState>();
  const tipo = watch("tipo");
  const showPressRelease = tipo === 1 || tipo === 3;
  const showArtigo = tipo === 3;

  const [files, setFiles] = useState<FileEntry[]>([]);

  const addFiles = useCallback((e: React.ChangeEvent<HTMLInputElement>, kind: string) => {
    const input = e.target;
    if (!input.files || input.files.length === 0) return;

    // Snapshot the FileList into a real array NOW: input.files is a live
    // reference that input.value = "" empties, and the state updater below runs
    // afterwards — iterating the live list there would yield nothing.
    const picked = Array.from(input.files);
    input.value = ""; // let the user re-pick the same file later

    setFiles((prev) => {
      const next = [...prev];
      for (const file of picked) {
        const existingIdx = next.findIndex((f) => f.kind === kind && f.file.name === file.name);
        const entry: FileEntry = { file, kind, id: `file-${++fileIdCounter}` };
        if (existingIdx >= 0) {
          next[existingIdx] = entry;
        } else {
          next.push(entry);
        }
      }
      return next;
    });
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  if (typeof window !== "undefined") {
    (window as any).__sigbah_attachments = files;
  }

  const kindFiles = (kind: string) => files.filter((f) => f.kind === kind);

  return (
    <section className="overflow-hidden rounded-xl bg-white shadow-[0_20px_50px_-40px_rgba(15,23,42,0.35)]">
      <div className="border-b border-slate-200 px-4 py-5 sm:px-8">
        <h2 className="text-2xl font-semibold tracking-tight text-slate-950">Anexos</h2>
      </div>

      <div className="space-y-5 px-4 py-6 sm:px-8 sm:py-8">
        <div>
          <div className="flex items-center gap-1">
            <IconUpload aria-hidden="true" size={18} stroke={1.9} className="shrink-0 text-sky-700" />
            <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">Documentos</h3>
          </div>
          <p className="mt-2 text-sm leading-6 text-slate-600">Envie os documentos obrigatórios conforme a resolução do programa.</p>
        </div>

        <FileField label="Currículo Lattes dos membros externos (PDF)" required multiple kind="lattes_cv" files={kindFiles("lattes_cv")} disabled={disabled} onAdd={addFiles} onRemove={removeFile} />

        <FileField label="Texto da dissertação/exame/tese (PDF)" required kind="texto" files={kindFiles("texto")} disabled={disabled} onAdd={addFiles} onRemove={removeFile} />

        {showPressRelease && (
          <FileField label="Press release (PDF)" required kind="press_release" files={kindFiles("press_release")} disabled={disabled} onAdd={addFiles} onRemove={removeFile} />
        )}

        {showArtigo && (
          <FileField label="Artigo publicado/aceito (PDF)" required kind="artigo" files={kindFiles("artigo")} disabled={disabled} onAdd={addFiles} onRemove={removeFile} />
        )}
      </div>
    </section>
  );
}

function FileField({ label, required, multiple, kind, files, disabled, onAdd, onRemove, hint }: {
  label: string;
  required?: boolean;
  multiple?: boolean;
  kind: string;
  files: FileEntry[];
  disabled: boolean;
  onAdd: (e: React.ChangeEvent<HTMLInputElement>, kind: string) => void;
  onRemove: (id: string) => void;
  hint?: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const statusText = files.length === 0
    ? "Nenhum arquivo selecionado"
    : `${files.length} arquivo${files.length > 1 ? "s" : ""} selecionado${files.length > 1 ? "s" : ""}`;

  // The picker is opened by a <button> that calls input.click() via a ref —
  // deliberately NOT a <label htmlFor>. A label (especially one wrapped by
  // another label) can dispatch a second click at the input, reopening the
  // dialog and silently dropping the chosen file.
  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1.5">
      <span className="text-sm font-semibold leading-5 text-slate-800">
        {label}
        {required ? <span className="ml-1 font-bold text-sky-700">*</span> : null}
      </span>
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={disabled}
          className={`inline-flex cursor-pointer items-center rounded-lg bg-sky-50 px-4 py-2 text-sm font-semibold text-sky-700 transition hover:bg-sky-100 ${disabled ? "pointer-events-none opacity-50" : ""}`}
        >
          Escolher arquivo{multiple ? "s" : ""}
        </button>
        <span className="text-sm text-slate-500">{statusText}</span>
        <input ref={inputRef} type="file" accept=".pdf" multiple={multiple} disabled={disabled} onChange={(e) => onAdd(e, kind)} className="hidden" />
      </div>
      {files.length > 0 && (
        <ul className="mt-2 space-y-1">
          {files.map((entry) => (
            <li key={entry.id} className="flex items-center gap-2 rounded bg-slate-100 px-3 py-1.5 text-sm text-slate-700">
              <span className="flex-1 truncate">{entry.file.name}</span>
              <span className="text-xs text-slate-400">{(entry.file.size / 1024).toFixed(0)} KB</span>
              <button type="button" onClick={() => onRemove(entry.id)} disabled={disabled} className="text-red-500 hover:text-red-700 disabled:text-slate-300">
                <IconX size={14} stroke={2} />
              </button>
            </li>
          ))}
        </ul>
      )}
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}
