import { useState } from "react";
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
    <div className="container">
      <h1>SigBah! — Nova Banca</h1>

      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)}>
          <BancaForm />

          {status && (
            <div className={status.ok ? "alert alert-ok" : "alert alert-err"}>
              {status.message}
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Enviando..." : "Enviar Pedido ao Coordenador"}
          </button>
        </form>
      </FormProvider>
    </div>
  );
}
