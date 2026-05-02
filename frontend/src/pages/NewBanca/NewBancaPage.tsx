import { useRef, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { FormProvider, useForm } from "react-hook-form";

import BancaForm, { serializeBanca } from "./BancaForm";
import { isDevelopment } from "../../env.js";
import {
  newBancaDefaultValues,
  newBancaFormStateSchema,
  type NewBancaFormState,
} from "../../types/new-banca.ts";
import { newBancaMockValues } from "./mock";

const FRESH_FORM: NewBancaFormState = isDevelopment
  ? newBancaMockValues
  : newBancaDefaultValues;

type ValidationDetail = {
  msg: string;
  loc: Array<string | number>;
};

type SubmitResponse = {
  ata?: number;
  student_name?: string;
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
          typeof item === "object" &&
          item !== null &&
          "msg" in item &&
          "loc" in item,
      )
      .map((item) => `${item.msg} (${item.loc.join(".")})`)
      .join("; ");
  }
  return typeof detail === "string" ? detail : "Erro ao enviar pedido.";
}

export default function NewBancaPage() {
  const form = useForm<NewBancaFormState>({
    defaultValues: FRESH_FORM,
    resolver: zodResolver(newBancaFormStateSchema),
  });
  const [status, setStatus] = useState<SubmitStatus | null>(null);
  const loading = form.formState.isSubmitting;
  const headerRef = useRef<HTMLElement | null>(null);

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
        setStatus({
          ok: true,
          message: `Pedido enviado ao coordenador. (Banca #${data.ata ?? "—"} — ${data.student_name ?? "—"})`,
        });
        form.reset(FRESH_FORM);
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
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl mb-4!">
            Solicitação de nova banca
          </h1>
        </header>

        <FormProvider {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-5"
          >
            <p className="text-sm leading-6 text-slate-500">
              Campos marcados com{" "}
              <span className="font-semibold text-sky-700">*</span> precisam ser
              preenchidos antes do envio.
            </p>

            {status && (
              <div
                className={
                  status.ok
                    ? "rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
                    : "rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900"
                }
              >
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
