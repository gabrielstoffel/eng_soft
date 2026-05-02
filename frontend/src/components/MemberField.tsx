import { IconX } from "@tabler/icons-react";
import { useFormContext } from "react-hook-form";

import { type NewBancaFormState } from "../types/new-banca.ts";
import Field from "./Field";
import SelectInput from "./SelectInput";
import TextInput from "./TextInput";
import type { MemberRole } from "../pages/NewBanca/config";

type MemberFieldProps = {
  label: string;
  name: MemberRole;
  required?: boolean;
  requireEmail?: boolean;
  disabled?: boolean;
  onRemove?: () => void;
};

export default function MemberField({
  label,
  name,
  required = false,
  requireEmail = false,
  disabled = false,
  onRemove,
}: MemberFieldProps) {
  const { register } = useFormContext<NewBancaFormState>();

  function parseGender(raw: string): 0 | 1 {
    return raw === "1" ? 1 : 0;
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 sm:p-5">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-950">{label}</h3>
          <p className="mt-1 text-sm text-slate-500">
            {required ? "Participante obrigatório nesta composição." : "Participante opcional adicionado à banca."}
          </p>
        </div>

        {onRemove ? (
          <button
            type="button"
            onClick={onRemove}
            disabled={disabled}
            className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium leading-none text-slate-700 transition hover:border-slate-400 hover:bg-slate-100 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
          >
            <IconX aria-hidden="true" size={15} stroke={2} className="shrink-0" />
            <span className="leading-none">Remover</span>
          </button>
        ) : (
          <span className="rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold tracking-[0.14em] text-sky-700 uppercase">
            Obrigatório
          </span>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <Field label="Tratamento" required>
          <SelectInput
            required
            disabled={disabled}
            {...register(`${name}.gender`, {
              setValueAs: (fieldValue) => parseGender(String(fieldValue)),
            })}
          >
            <option value={0}>Prof. Dr.</option>
            <option value={1}>Profª. Drª.</option>
          </SelectInput>
        </Field>

        <Field label="Nome" required>
          <TextInput
            type="text"
            required
            disabled={disabled}
            {...register(`${name}.name`)}
          />
        </Field>

        <Field label="Instituição" required>
          <TextInput
            type="text"
            required
            disabled={disabled}
            {...register(`${name}.institution`)}
          />
        </Field>

        <Field label="Localidade" required>
          <TextInput
            type="text"
            required
            disabled={disabled}
            {...register(`${name}.location`)}
          />
        </Field>

        <Field label="Idioma da carta" required>
          <SelectInput
            required
            disabled={disabled}
            {...register(`${name}.lang`)}
          >
            <option value="pt">Português</option>
            <option value="en">English</option>
          </SelectInput>
        </Field>

        <Field label="E-mail" required={requireEmail}>
          <TextInput
            type="email"
            required={requireEmail}
            disabled={disabled}
            placeholder="email@instituicao.br"
            {...register(`${name}.email`)}
          />
        </Field>
      </div>
    </section>
  );
}
