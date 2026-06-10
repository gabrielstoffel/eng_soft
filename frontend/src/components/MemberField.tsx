import { IconTrash } from "@tabler/icons-react";
import { useFormContext } from "react-hook-form";

import type { NewBancaFormState, Ppg } from "../types/new-banca.ts";
import Field from "./Field";
import SelectInput from "./SelectInput";
import TextInput from "./TextInput";

type MemberFieldProps = {
  label: string;
  name: string;
  required?: boolean;
  requireEmail?: boolean;
  disabled?: boolean;
  ppg?: Ppg;
  onRemove?: () => void;
};

export default function MemberField({
  label,
  name,
  required = false,
  requireEmail = false,
  disabled = false,
  ppg = "ppgfis",
  onRemove,
}: MemberFieldProps) {
  const { register, formState: { errors } } = useFormContext<NewBancaFormState>();
  const prefix = name as keyof NewBancaFormState;
  const fieldErrors = (errors as any)[prefix];

  const showPpgEnfisFields = ppg === "ppgenfis";

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-slate-800">
          {label}
          {required && <span className="ml-1 text-red-500">*</span>}
        </h4>
        {onRemove && (
          <button type="button" onClick={onRemove} disabled={disabled} className="inline-flex cursor-pointer items-center gap-1 rounded px-2 py-1 text-xs text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:text-slate-400">
            <IconTrash size={14} stroke={1.8} />
            Remover
          </button>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="Tratamento" required={required}>
          <SelectInput required={required} disabled={disabled} {...register(`${prefix}.gender` as any, { setValueAs: (v: string) => (v === "1" ? 1 : 0) })}>
            <option value={0}>Prof. Dr.</option>
            <option value={1}>Profª. Drª.</option>
          </SelectInput>
        </Field>

        <Field label="Nome completo" required={required}>
          <TextInput type="text" required={required} disabled={disabled} {...register(`${prefix}.name` as any)} />
        </Field>

        <Field label="Instituição" required={required}>
          <TextInput type="text" required={required} disabled={disabled} {...register(`${prefix}.institution` as any)} />
        </Field>

        <Field label="Cidade/Estado" required={required}>
          <TextInput type="text" required={required} disabled={disabled} {...register(`${prefix}.location` as any)} />
        </Field>

        <Field label="Idioma preferencial" required={required}>
          <SelectInput required={required} disabled={disabled} {...register(`${prefix}.lang` as any)}>
            <option value="pt">Português</option>
            <option value="en">English</option>
          </SelectInput>
        </Field>

        <Field label="E-mail" required={requireEmail} error={fieldErrors?.email?.message}>
          <TextInput type="email" required={requireEmail} disabled={disabled} hasError={!!fieldErrors?.email} {...register(`${prefix}.email` as any)} />
        </Field>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" disabled={disabled} {...register(`${prefix}.remoto` as any)} className="rounded border-slate-300" />
            Participação remota
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" disabled={disabled} {...register(`${prefix}.bolsista_cnpq` as any)} className="rounded border-slate-300" />
            Bolsista CNPq
          </label>
        </div>

        <Field label="Nível CNPq">
          <TextInput type="text" disabled={disabled} placeholder="1A, 1B, 2..." {...register(`${prefix}.nivel_cnpq` as any)} />
        </Field>

        {showPpgEnfisFields && (
          <>
            <Field label="Lattes" required>
              <TextInput type="url" required disabled={disabled} placeholder="http://lattes.cnpq.br/..." {...register(`${prefix}.lattes` as any)} />
            </Field>
            <Field label="Instituição conclusão doutorado" required>
              <TextInput type="text" required disabled={disabled} {...register(`${prefix}.doctorate_institution` as any)} />
            </Field>
            <Field label="Ano conclusão doutorado" required>
              <TextInput type="text" required disabled={disabled} placeholder="2015" {...register(`${prefix}.doctorate_year` as any)} />
            </Field>
          </>
        )}
      </div>
    </div>
  );
}
