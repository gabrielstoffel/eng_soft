import { useRef, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { FormProvider, useForm } from "react-hook-form";

import BancaForm, { scrollToFirstError, serializeBanca } from "./form/BancaForm";
import { newBancaMockValues, newBancaMockValuesEnfis } from "./mock.ts";
import {
  newBancaDefaultValues,
  newBancaFormStateSchema,
  type NewBancaFormState,
  type Ppg,
} from "../../types/new-banca.ts";
import { isDevelopment } from "../../env.js";

type ValidationDetail = {
  msg: string;
  loc: Array<string | number>;
};

type SubmitResponse = {
  ata?: number;
  student_name?: string;
  decision_token?: string;
  detail?: unknown;
};

type SubmitStatus =
  | { ok: true; message: string }
  | { ok: false; message: string };

function formatErrorDetail(detail: unknown): string {
  if (Array.isArray(detail)) {
    return detail
      .filter(
        (item): item is ValidationDetail =>
          typeof item === "object" && item !== null && "msg" in item && "loc" in item,
      )
      .map((item) => `${item.msg} (${item.loc.join(".")})`)
      .join("; ");
  }
  return typeof detail === "string" ? detail : "Erro ao enviar pedido.";
}

const PPG_LABELS: Record<Ppg, string> = {
  ppgfis: "PPGFís",
  ppgenfis: "PPGEnFis",
};

const GENERIC_VALIDATION_MESSAGE = "Há campos obrigatórios não preenchidos.";

const MAX_UPLOAD_BYTES = 150 * 1024 * 1024; // 150 MB total across all attachments

type NewBancaPageProps = {
  ppg: Ppg;
};

export default function NewBancaPage({ ppg }: NewBancaPageProps) {
  const freshForm = newBancaDefaultValues(ppg);
  // In dev (`npm run dev`), start with every field prefilled so the form can be
  // submitted without retyping — each PPG has its own mock. Production starts blank.
  const initialForm = isDevelopment
    ? (ppg === "ppgenfis" ? newBancaMockValuesEnfis : newBancaMockValues)
    : freshForm;

  const form = useForm<NewBancaFormState>({
    defaultValues: initialForm,
    resolver: zodResolver(newBancaFormStateSchema),
    shouldFocusError: false, // we scroll to the first error ourselves (smoothly)
  });
  const [status, setStatus] = useState<SubmitStatus | null>(null);
  const loading = form.formState.isSubmitting;
  const headerRef = useRef<HTMLElement | null>(null);

  async function handleSubmit(values: NewBancaFormState) {
    setStatus(null);
    const body = serializeBanca(values);

    // Send the petition and its PDF attachments in one multipart request so the
    // files can be attached to the email sent to the coordenador.
    const formData = new FormData();
    formData.append("payload", JSON.stringify(body));
    const entries: Array<{ file: File; kind: string }> = (window as any).__sigbah_attachments || [];

    const totalBytes = entries.reduce((sum, e) => sum + (e.file?.size ?? 0), 0);
    if (totalBytes > MAX_UPLOAD_BYTES) {
      setStatus({ ok: false, message: "Os anexos excedem o limite de 150 MB." });
      return;
    }

    for (const { file, kind } of entries) {
      formData.append("files", file);
      formData.append("kinds", kind);
    }

    try {
      const res = await fetch("/banca", {
        method: "POST",
        body: formData,
      });
      const data: SubmitResponse = await res.json();
      if (res.ok) {
        setStatus({
          ok: true,
          message: `Pedido enviado ao coordenador. (Banca #${data.ata ?? "—"} — ${data.student_name ?? "—"})`,
        });
        form.reset(freshForm);
      } else if (res.status === 422) {
        // Field-level validation: highlight the offending fields rather than
        // exposing backend field details.
        setStatus({ ok: false, message: GENERIC_VALIDATION_MESSAGE });
      } else {
        setStatus({ ok: false, message: formatErrorDetail(data.detail) });
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Erro desconhecido";
      setStatus({ ok: false, message: `Erro de conexão: ${message}` });
    }
  }

  // Client-side validation failed: the offending fields are already outlined in
  // red — just point the user to them without naming any field.
  function handleInvalid() {
    setStatus({ ok: false, message: GENERIC_VALIDATION_MESSAGE });
    scrollToFirstError();
  }

  return (
    <div className="min-h-screen bg-stone-100 text-slate-900">
      <div className="mx-auto w-full max-w-6xl px-3 py-8 sm:px-6 lg:px-8 lg:py-10">
        <header ref={headerRef}>
          <div className="text-xs font-semibold tracking-[0.18em] text-sky-700 uppercase">{PPG_LABELS[ppg]}</div>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl mb-4!">
            Solicitação de nova banca
          </h1>
        </header>

        <FormProvider {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit, handleInvalid)} className="space-y-5">
            <p className="text-sm leading-6 text-slate-500">
              Campos marcados com <span className="font-semibold text-sky-700">*</span> precisam ser preenchidos antes do envio.
            </p>

            {status && (
              <div className={status.ok
                ? "rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
                : "rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900"
              }>
                {status.message}
              </div>
            )}

            <BancaForm
              loading={loading}
              submittedSuccessfully={status?.ok === true}
              scrollTargetRef={headerRef}
            />
          </form>
        </FormProvider>
      </div>
    </div>
  );
}
