import { useRef, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { FormProvider, useForm } from "react-hook-form";

import BancaForm, { serializeBanca } from "./form/BancaForm";
import {
  newBancaDefaultValues,
  newBancaFormStateSchema,
  type NewBancaFormState,
  type Ppg,
} from "../../types/new-banca.ts";

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

type NewBancaPageProps = {
  ppg: Ppg;
};

export default function NewBancaPage({ ppg }: NewBancaPageProps) {
  const freshForm = newBancaDefaultValues(ppg);

  const form = useForm<NewBancaFormState>({
    defaultValues: freshForm,
    resolver: zodResolver(newBancaFormStateSchema),
  });
  const [status, setStatus] = useState<SubmitStatus | null>(null);
  const loading = form.formState.isSubmitting;
  const headerRef = useRef<HTMLElement | null>(null);

  async function uploadAttachments(token: string) {
    const entries: Array<{ file: File; kind: string }> = (window as any).__sigbah_attachments || [];
    if (entries.length === 0) return;

    const formData = new FormData();
    for (const { file, kind } of entries) {
      formData.append("files", file);
      formData.append("kinds", kind);
    }

    await fetch(`/banca/${token}/attachments`, {
      method: "POST",
      body: formData,
    });
  }

  async function handleSubmit(values: NewBancaFormState) {
    setStatus(null);
    const body = serializeBanca(values);

    try {
      const res = await fetch("/banca", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data: SubmitResponse = await res.json();
      if (res.ok) {
        // Upload attachments if any
        const token = data.decision_token;
        if (token) {
          await uploadAttachments(token);
        }
        setStatus({
          ok: true,
          message: `Pedido enviado ao coordenador. (Banca #${data.ata ?? "—"} — ${data.student_name ?? "—"})`,
        });
        form.reset(freshForm);
      } else {
        setStatus({ ok: false, message: formatErrorDetail(data.detail) });
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Erro desconhecido";
      setStatus({ ok: false, message: `Erro de conexão: ${message}` });
    }
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
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-5">
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
