import { useEffect, useState } from "react";
import { useFormContext } from "react-hook-form";

import { ROLES_BY_TIPO } from "../config";
import BancaCompositionSection from "./BancaCompositionSection";
import BancaGeneralSection from "./BancaGeneralSection";
import {
  emptyMemberForm,
  newBancaDefaultValues,
  serializeNewBancaForm,
  type BancaRequest,
  type MemberInfo,
  type NewBancaFormState,
} from "../../../types/new-banca.ts";

export const EMPTY_MEMBER = emptyMemberForm;

export const INITIAL_FORM = newBancaDefaultValues;

export function serializeBanca(form: NewBancaFormState): BancaRequest {
  const roles = ROLES_BY_TIPO[form.tipo];

  return serializeNewBancaForm({
    ...form,
    coorientador: roles.coorientador === "hidden" ? null : form.coorientador,
    externo1: roles.externo1 === "hidden" ? null : form.externo1,
    externo2: roles.externo2 === "hidden" ? null : form.externo2,
    interno1: roles.interno1 === "hidden" ? null : form.interno1,
    interno2: roles.interno2 === "hidden" ? null : form.interno2,
    supl_int: roles.supl_int === "hidden" ? null : form.supl_int,
    supl_ext: roles.supl_ext === "hidden" ? null : form.supl_ext,
  });
}

export function deserializeBanca(req: BancaRequest): NewBancaFormState {
  const fillMember = (m: MemberInfo | null) =>
    m ? { ...EMPTY_MEMBER, ...m, email: m.email ?? "" } : null;

  return {
    nome: { gender: req.nome.gender, name: req.nome.name },
    tipo: req.tipo,
    data: req.data || "",
    horario: req.horario || "",
    data_convite: req.data_convite || "",
    ata: String(req.ata),
    local_banca: req.local_banca || "",
    link: req.link || "",
    titulo: req.titulo,
    titulo2: req.titulo2,
    orientador: fillMember(req.orientador) ?? { ...EMPTY_MEMBER },
    coorientador: fillMember(req.coorientador),
    externo1: fillMember(req.externo1),
    externo2: fillMember(req.externo2),
    interno1: fillMember(req.interno1),
    interno2: fillMember(req.interno2),
    supl_int: fillMember(req.supl_int),
    supl_ext: fillMember(req.supl_ext),
  };
}

type BancaFormProps = {
  disabled?: boolean;
  loading?: boolean;
  submittedSuccessfully?: boolean;
  scrollTargetRef?: React.RefObject<HTMLElement | null>;
};

const STEP_ONE_FIELDS = [
  "nome.gender",
  "nome.name",
  "tipo",
  "ata",
  "data",
  "horario",
  "data_convite",
  "local_banca",
  "link",
  "titulo",
  "titulo2",
] as const;

export default function BancaForm({
  disabled = false,
  loading = false,
  submittedSuccessfully = false,
  scrollTargetRef,
}: BancaFormProps) {
  const { trigger } = useFormContext<NewBancaFormState>();
  const [step, setStep] = useState<1 | 2>(1);

  useEffect(() => {
    if (submittedSuccessfully) {
      setStep(1);
    }
  }, [submittedSuccessfully]);

  useEffect(() => {
    const id = window.requestAnimationFrame(() => {
      scrollTargetRef?.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });

    return () => window.cancelAnimationFrame(id);
  }, [scrollTargetRef, step]);

  async function goToComposition() {
    const isValid = await trigger(STEP_ONE_FIELDS);
    if (!isValid) return;
    setStep(2);
  }

  return (
    <div className="space-y-5">
      {step === 1 ? (
        <>
          <BancaGeneralSection disabled={disabled} />

          <div className="flex justify-end">
            <button
              type="button"
              onClick={goToComposition}
              disabled={disabled}
              className="inline-flex w-full cursor-pointer items-center justify-center rounded-xl bg-sky-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              Continuar
            </button>
          </div>
        </>
      ) : (
        <>
          <BancaCompositionSection disabled={disabled} />

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={() => setStep(1)}
              disabled={loading}
              className="inline-flex w-full cursor-pointer items-center justify-center rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400 sm:w-1/2"
            >
              Voltar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full cursor-pointer items-center justify-center rounded-xl bg-sky-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-1/2"
            >
              {loading ? "Enviando..." : "Enviar"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
