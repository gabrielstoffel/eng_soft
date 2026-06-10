import {
  IconCalendarEvent,
  IconFileDescription,
  IconMessage,
  IconUserSquareRounded,
} from "@tabler/icons-react";
import { useFormContext } from "react-hook-form";

import {
  bancaTypeLabelByValue,
  emptyMemberForm,
  genderLabelByValue,
  modalidadeLabelByValue,
  type NewBancaFormState,
} from "../../../types/new-banca.ts";
import {
  OPTIONAL_MEMBER_ROLES,
  ROLES_BY_TIPO,
  type OptionalMemberRole,
} from "../config";
import Field from "../../../components/Field";
import SelectInput from "../../../components/SelectInput";
import TextInput from "../../../components/TextInput";

type BancaGeneralSectionProps = {
  disabled?: boolean;
};

export default function BancaGeneralSection({
  disabled = false,
}: BancaGeneralSectionProps) {
  const { register, setValue, watch, formState: { errors } } = useFormContext<NewBancaFormState>();
  const form = watch();
  const ppg = form.ppg;

  function parseGender(value: string): 0 | 1 {
    return value === "1" ? 1 : 0;
  }

  function parseBancaType(value: string): NewBancaFormState["tipo"] {
    if (value === "2") return 2;
    if (value === "3") return 3;
    return 1;
  }

  function setOptionalMember(
    role: OptionalMemberRole,
    value: NewBancaFormState[OptionalMemberRole],
  ) {
    setValue(role, value);
  }

  function changeTipo(newTipo: NewBancaFormState["tipo"]) {
    const newRoles = ROLES_BY_TIPO[ppg][newTipo];
    setValue("tipo", newTipo);
    for (const role of OPTIONAL_MEMBER_ROLES) {
      if (newRoles[role] === "required" && !form[role]) {
        setOptionalMember(role, { ...emptyMemberForm });
      }
      if (newRoles[role] === "hidden") {
        setOptionalMember(role, null);
      }
    }
  }

  const modalidade = form.modalidade;
  const showSala = modalidade === "presencial" || modalidade === "hibrida";
  const showLink = modalidade === "remota" || modalidade === "hibrida";

  return (
    <section className="overflow-hidden rounded-xl bg-white shadow-[0_20px_50px_-40px_rgba(15,23,42,0.35)]">
      <div className="border-b border-slate-200 px-4 py-5 sm:px-8">
        <div className="text-xs font-semibold tracking-[0.18em] text-sky-700 uppercase">
          Etapa 1 de 2
        </div>
        <h2 className="mt-1 text-2xl font-semibold tracking-tight mb-0! pb-0! text-slate-950">
          Identificação da banca e agenda da defesa
        </h2>
      </div>

      <div className="space-y-8 px-4 py-6 sm:px-8 sm:py-8">
        {/* Identificação */}
        <div className="space-y-4 border-b border-slate-200 pb-8">
          <div>
            <div className="flex items-center gap-1">
              <IconUserSquareRounded aria-hidden="true" size={18} stroke={1.9} className="shrink-0 self-center text-sky-700" />
              <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">Identificação</h3>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">Dados do aluno e enquadramento formal da sessão.</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-[12rem_minmax(0,1fr)]">
            <Field label="Tratamento" required>
              <SelectInput required disabled={disabled} {...register("nome.gender", { setValueAs: (v) => parseGender(String(v)) })}>
                <option value={0}>{genderLabelByValue[0]}</option>
                <option value={1}>{genderLabelByValue[1]}</option>
              </SelectInput>
            </Field>
            <Field label="Nome do(a) aluno(a)" required error={errors.nome?.name?.message}>
              <TextInput type="text" required disabled={disabled} hasError={!!errors.nome?.name} {...register("nome.name")} />
            </Field>
          </div>

          {ppg === "ppgenfis" && (
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="CPF" required>
                <TextInput type="text" required disabled={disabled} {...register("nome.cpf")} />
              </Field>
              <Field label="Data de nascimento" required>
                <TextInput type="date" required disabled={disabled} {...register("nome.birth_date")} />
              </Field>
              <Field label="E-mail do aluno" required>
                <TextInput type="email" required disabled={disabled} {...register("nome.email")} />
              </Field>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-1">
            <Field label="Tipo" required>
              <SelectInput required disabled={disabled} {...register("tipo", { setValueAs: (v) => parseBancaType(String(v)), onChange: (e) => changeTipo(parseBancaType(e.target.value)) })}>
                <option value={1}>{bancaTypeLabelByValue[1]}</option>
                <option value={2}>{bancaTypeLabelByValue[2]}</option>
                <option value={3}>{bancaTypeLabelByValue[3]}</option>
              </SelectInput>
            </Field>
          </div>
        </div>

        {/* Agenda */}
        <div className="space-y-4 border-b border-slate-200 pb-8">
          <div>
            <div className="flex items-center gap-1">
              <IconCalendarEvent aria-hidden="true" size={18} stroke={1.9} className="shrink-0 self-center text-sky-700" />
              <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">Agenda</h3>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">Data, horário e logística da defesa.</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <Field label="Data sugerida" required error={errors.data?.message}>
              <TextInput type="date" required disabled={disabled} hasError={!!errors.data} {...register("data")} />
            </Field>
            <Field label="Horário sugerido" required error={errors.horario?.message}>
              <TextInput type="time" required disabled={disabled} hasError={!!errors.horario} {...register("horario")} />
            </Field>
            <Field label="Modalidade" required>
              <SelectInput required disabled={disabled} {...register("modalidade")}>
                {Object.entries(modalidadeLabelByValue).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </SelectInput>
            </Field>
          </div>

          {showSala && (
            <Field label="Sala de preferência" required>
              <TextInput type="text" required disabled={disabled} placeholder="Ex: Sala de videoconferências, Anfiteatro..." {...register("sala_preferencia")} />
            </Field>
          )}

          {showLink && (
            <Field label="Link de videoconferência">
              <TextInput type="url" disabled={disabled} placeholder="https:// (preencha se já disponível)" {...register("link")} />
            </Field>
          )}
        </div>

        {/* Títulos */}
        <div className="space-y-4 border-b border-slate-200 pb-8">
          <div>
            <div className="flex items-center gap-1">
              <IconFileDescription aria-hidden="true" size={18} stroke={1.9} className="shrink-0 self-center text-sky-700" />
              <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">Títulos</h3>
            </div>
          </div>

          <div className="grid gap-4">
            <Field label="Título em português" required error={errors.titulo?.message}>
              <TextInput type="text" required disabled={disabled} hasError={!!errors.titulo} {...register("titulo")} />
            </Field>
            <Field label="Título em inglês">
              <TextInput type="text" disabled={disabled} {...register("titulo2")} />
            </Field>
          </div>
        </div>

        {/* Comentários */}
        <div className="space-y-4">
          <div>
            <div className="flex items-center gap-1">
              <IconMessage aria-hidden="true" size={18} stroke={1.9} className="shrink-0 self-center text-sky-700" />
              <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">Comentários</h3>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">Informações enviadas ao coordenador para avaliação do mérito.</p>
          </div>

          <Field label="Comentários sobre o desempenho do estudante">
            <textarea disabled={disabled} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:ring-1 focus:ring-sky-500 disabled:bg-slate-50" {...register("comentario_desempenho")} />
          </Field>

          <Field label="Justificativa para a escolha dos membros">
            <textarea disabled={disabled} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-sky-500 focus:ring-1 focus:ring-sky-500 disabled:bg-slate-50" {...register("justificativa_membros")} />
          </Field>
        </div>
      </div>
    </section>
  );
}
