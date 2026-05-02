import { useFormContext } from 'react-hook-form'

import MemberField from './MemberField'
import {
  ALL_ROLES,
  OPTIONAL_MEMBER_ROLES,
  ROLE_LABELS,
  ROLES_BY_TIPO,
  type OptionalMemberRole,
} from './config'
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
} from '../../types/new-banca.ts'

export const EMPTY_MEMBER = emptyMemberForm

export const INITIAL_FORM = newBancaDefaultValues

export function serializeBanca(form: NewBancaFormState): BancaRequest {
  const roles = ROLES_BY_TIPO[form.tipo]

  return serializeNewBancaForm({
    ...form,
    coorientador: roles.coorientador === 'hidden' ? null : form.coorientador,
    externo1: roles.externo1 === 'hidden' ? null : form.externo1,
    externo2: roles.externo2 === 'hidden' ? null : form.externo2,
    interno1: roles.interno1 === 'hidden' ? null : form.interno1,
    interno2: roles.interno2 === 'hidden' ? null : form.interno2,
    supl_int: roles.supl_int === 'hidden' ? null : form.supl_int,
    supl_ext: roles.supl_ext === 'hidden' ? null : form.supl_ext,
  })
}

// Convert a backend BancaRequest payload into the form-friendly shape used by INITIAL_FORM
// (date/time strings as plain strings, missing optional members rendered as null).
export function deserializeBanca(req: BancaRequest): NewBancaFormState {
  const fillMember = (m: MemberInfo | null): MemberForm | null =>
    m ? { ...EMPTY_MEMBER, ...m, email: m.email ?? '' } : null

  return {
    nome: { gender: req.nome.gender, name: req.nome.name },
    tipo: req.tipo,
    data: req.data || '',
    horario: req.horario || '',
    data_convite: req.data_convite || '',
    ata: String(req.ata),
    local_banca: req.local_banca || '',
    link: req.link || '',
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
  }
}

type BancaFormProps = {
  disabled?: boolean
}

export default function BancaForm({ disabled = false }: BancaFormProps) {
  const { register, setValue, watch } = useFormContext<NewBancaFormState>()
  const form = watch()

  function parseGender(value: string): 0 | 1 {
    return value === '1' ? 1 : 0
  }

  function parseBancaType(value: string): NewBancaFormState['tipo'] {
    if (value === '2') return 2
    if (value === '3') return 3
    return 1
  }

  function setOptionalMember(role: OptionalMemberRole, value: MemberForm | null) {
    setValue(role, value)
  }

  function changeTipo(newTipo: NewBancaFormState['tipo']) {
    const newRoles = ROLES_BY_TIPO[newTipo]
    setValue('tipo', newTipo)
    for (const role of OPTIONAL_MEMBER_ROLES) {
      if (newRoles[role] === 'required' && !form[role]) {
        setOptionalMember(role, { ...EMPTY_MEMBER })
      }
      if (newRoles[role] === 'hidden') {
        setOptionalMember(role, null)
      }
    }
  }

  const visibleRoles = ROLES_BY_TIPO[form.tipo]

  return (
    <>
      <section>
        <h2>Dados Gerais</h2>

        <div className="row">
          <label>
            Tratamento do(a) aluno(a) *
            <select
              required
              disabled={disabled}
              {...register('nome.gender', {
                setValueAs: (value) => parseGender(String(value)),
              })}
            >
              <option value={0}>{genderLabelByValue[0]}</option>
              <option value={1}>{genderLabelByValue[1]}</option>
            </select>
          </label>

          <label>
            Nome do(a) aluno(a) *
            <input
              type="text"
              required
              disabled={disabled}
              {...register('nome.name')}
            />
          </label>
        </div>

        <div className="row">
          <label>
            Tipo *
            <select
              required
              disabled={disabled}
              {...register('tipo', {
                onChange: (e) => changeTipo(parseBancaType(e.target.value)),
              })}
            >
              <option value={1}>{bancaTypeLabelByValue[1]}</option>
              <option value={2}>{bancaTypeLabelByValue[2]}</option>
              <option value={3}>{bancaTypeLabelByValue[3]}</option>
            </select>
          </label>

          <label>
            Número da Ata *
            <input
              type="number"
              required
              min={1}
              disabled={disabled}
              {...register('ata')}
            />
          </label>
        </div>

        <div className="row">
          <label>
            Data da defesa *
            <input
              type="date"
              required
              disabled={disabled}
              {...register('data')}
            />
          </label>

          <label>
            Horário *
            <input
              type="time"
              required
              disabled={disabled}
              {...register('horario')}
            />
          </label>

          <label>
            Data dos convites
            <input
              type="date"
              disabled={disabled}
              {...register('data_convite')}
            />
          </label>
        </div>

        <div className="row">
          <label>
            Local
            <input
              type="text"
              disabled={disabled}
              {...register('local_banca')}
            />
          </label>

          <label>
            Link (videoconferência)
            <input
              type="url"
              disabled={disabled}
              {...register('link')}
            />
          </label>
        </div>

        <label>
          Título (PT) *
          <input
            type="text"
            required
            disabled={disabled}
            {...register('titulo')}
          />
        </label>

        <label>
          Título (EN) *
          <input
            type="text"
            required
            disabled={disabled}
            {...register('titulo2')}
          />
        </label>
      </section>

      <section>
        <h2>Composição da Banca</h2>

        {ALL_ROLES.map((role) =>
          visibleRoles[role] === 'hidden' ? null : (
            <MemberField
              key={role}
              label={ROLE_LABELS[role]}
              name={role}
              required={visibleRoles[role] === 'required'}
              requireEmail={role === 'orientador'}
              disabled={disabled}
            />
          ),
        )}
      </section>
    </>
  )
}
