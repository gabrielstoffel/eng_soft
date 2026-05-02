import { useFormContext } from "react-hook-form";

import Field from "./Field";
import MemberField from "./MemberField";
import SelectInput from "./SelectInput";
import TextInput from "./TextInput";
import {
  ALL_ROLES,
  OPTIONAL_MEMBER_ROLES,
  ROLE_LABELS,
  ROLES_BY_TIPO,
  type OptionalMemberRole,
} from "./config";
import {
  bancaTypeLabelByValue,
  emptyMemberForm,
  genderLabelByValue,
  newBancaDefaultValues,
  serializeNewBancaForm,
  type BancaRequest,
  type MemberForm,
  type MemberInfo,
  type NewBancaFormState,
} from "../../types/new-banca.ts";

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
  const fillMember = (m: MemberInfo | null): MemberForm | null =>
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
};

export default function BancaForm({ disabled = false }: BancaFormProps) {
  const { register, setValue, watch } = useFormContext<NewBancaFormState>();
  const form = watch();

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
    value: MemberForm | null,
  ) {
    setValue(role, value);
  }

  function changeTipo(newTipo: NewBancaFormState["tipo"]) {
    const newRoles = ROLES_BY_TIPO[newTipo];
    setValue("tipo", newTipo);
    for (const role of OPTIONAL_MEMBER_ROLES) {
      if (newRoles[role] === "required" && !form[role]) {
        setOptionalMember(role, { ...EMPTY_MEMBER });
      }
      if (newRoles[role] === "hidden") {
        setOptionalMember(role, null);
      }
    }
  }

  const visibleRoles = ROLES_BY_TIPO[form.tipo];

  return (
    <>
      <section className="overflow-hidden rounded-xl bg-white shadow-[0_20px_50px_-40px_rgba(15,23,42,0.35)]">
        <div className="border-b border-slate-200 px-4 py-5 sm:px-8">
          <div className="text-xs font-semibold tracking-[0.18em] text-sky-700 uppercase">
            Dados Gerais
          </div>
          <h2 className="mt-1 text-2xl font-semibold tracking-tight mb-0! pb-0! text-slate-950">
            Identificação da banca e agenda da defesa
          </h2>
        </div>

        <div className="space-y-8 px-4 py-6 sm:px-8 sm:py-8">
          <div className="space-y-4 border-b border-slate-200 pb-8">
            <div>
              <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">
                Identificação
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Dados do aluno e enquadramento formal da sessão.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-[12rem_minmax(0,1fr)]">
              <Field label="Tratamento" required>
                <SelectInput
                  required
                  disabled={disabled}
                  {...register("nome.gender", {
                    setValueAs: (value) => parseGender(String(value)),
                  })}
                >
                  <option value={0}>{genderLabelByValue[0]}</option>
                  <option value={1}>{genderLabelByValue[1]}</option>
                </SelectInput>
              </Field>

              <Field label="Nome do(a) aluno(a)" required>
                <TextInput
                  type="text"
                  required
                  disabled={disabled}
                  {...register("nome.name")}
                />
              </Field>
            </div>

            <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_11rem]">
              <Field label="Tipo" required>
                <SelectInput
                  required
                  disabled={disabled}
                  {...register("tipo", {
                    onChange: (e) => changeTipo(parseBancaType(e.target.value)),
                  })}
                >
                  <option value={1}>{bancaTypeLabelByValue[1]}</option>
                  <option value={2}>{bancaTypeLabelByValue[2]}</option>
                  <option value={3}>{bancaTypeLabelByValue[3]}</option>
                </SelectInput>
              </Field>

              <Field label="Ata" required>
                <TextInput
                  type="number"
                  required
                  min={1}
                  disabled={disabled}
                  {...register("ata")}
                />
              </Field>
            </div>
          </div>

          <div className="space-y-4 border-b border-slate-200 pb-8">
            <div>
              <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">
                Agenda
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Data, horário e referências de logística para a realização da
                defesa.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Data da defesa" required>
                <TextInput
                  type="date"
                  required
                  disabled={disabled}
                  {...register("data")}
                />
              </Field>

              <Field label="Horário" required>
                <TextInput
                  type="time"
                  required
                  disabled={disabled}
                  {...register("horario")}
                />
              </Field>

              <Field label="Data dos convites">
                <TextInput
                  type="date"
                  disabled={disabled}
                  {...register("data_convite")}
                />
              </Field>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Local">
                <TextInput
                  type="text"
                  disabled={disabled}
                  {...register("local_banca")}
                />
              </Field>

              <Field label="Link de videoconferência">
                <TextInput
                  type="url"
                  disabled={disabled}
                  placeholder="https://"
                  {...register("link")}
                />
              </Field>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">
                Títulos
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Estes campos são usados diretamente nos documentos oficiais
                emitidos pelo sistema.
              </p>
            </div>

            <div className="grid gap-4">
              <Field label="Título em português" required>
                <TextInput
                  type="text"
                  required
                  disabled={disabled}
                  {...register("titulo")}
                />
              </Field>

              <Field label="Título em inglês" required>
                <TextInput
                  type="text"
                  required
                  disabled={disabled}
                  {...register("titulo2")}
                />
              </Field>
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2>Composição da Banca</h2>

        {ALL_ROLES.map((role) =>
          visibleRoles[role] === "hidden" ? null : (
            <MemberField
              key={role}
              label={ROLE_LABELS[role]}
              name={role}
              required={visibleRoles[role] === "required"}
              requireEmail={role === "orientador"}
              disabled={disabled}
            />
          ),
        )}
      </section>
    </>
  );
}
