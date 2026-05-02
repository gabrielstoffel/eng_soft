import { useFormContext } from 'react-hook-form'

import MemberField from '../../MemberField.jsx'
import {
  ALL_ROLES,
  OPTIONAL_MEMBER_ROLES,
  ROLE_LABELS,
  ROLES_BY_TIPO,
  type MemberRole,
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
  const { setValue, watch } = useFormContext<NewBancaFormState>()
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

  function setMember(role: MemberRole, value: MemberForm | null) {
    if (role === 'orientador') {
      if (value) {
        setValue('orientador', value)
      }
      return
    }

    setOptionalMember(role, value)
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
            Tratamento do(a) aluno(a)
            <select
              value={form.nome.gender}
              disabled={disabled}
              onChange={(e) => setValue('nome', { ...form.nome, gender: parseGender(e.target.value) })}
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
              value={form.nome.name}
              onChange={(e) => setValue('nome', { ...form.nome, name: e.target.value })}
            />
          </label>
        </div>

        <div className="row">
          <label>
            Tipo *
            <select
              value={form.tipo}
              disabled={disabled}
              onChange={(e) => changeTipo(parseBancaType(e.target.value))}
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
              value={form.ata}
              onChange={(e) => setValue('ata', e.target.value)}
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
              value={form.data}
              onChange={(e) => setValue('data', e.target.value)}
            />
          </label>

          <label>
            Horário *
            <input
              type="time"
              required
              disabled={disabled}
              value={form.horario}
              onChange={(e) => setValue('horario', e.target.value)}
            />
          </label>

          <label>
            Data dos convites
            <input
              type="date"
              disabled={disabled}
              value={form.data_convite}
              onChange={(e) => setValue('data_convite', e.target.value)}
            />
          </label>
        </div>

        <div className="row">
          <label>
            Local
            <input
              type="text"
              disabled={disabled}
              value={form.local_banca}
              onChange={(e) => setValue('local_banca', e.target.value)}
            />
          </label>

          <label>
            Link (videoconferência)
            <input
              type="url"
              disabled={disabled}
              value={form.link}
              onChange={(e) => setValue('link', e.target.value)}
            />
          </label>
        </div>

        <label>
          Título (PT) *
          <input
            type="text"
            required
            disabled={disabled}
            value={form.titulo}
            onChange={(e) => setValue('titulo', e.target.value)}
          />
        </label>

        <label>
          Título (EN) *
          <input
            type="text"
            required
            disabled={disabled}
            value={form.titulo2}
            onChange={(e) => setValue('titulo2', e.target.value)}
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
              value={form[role]}
              onChange={(value: MemberForm | null) => setMember(role, value)}
              required={visibleRoles[role] === 'required'}
              requireEmail={role === 'orientador' || role.startsWith('externo') || role.startsWith('supl_')}
              disabled={disabled}
            />
          ),
        )}
      </section>
    </>
  )
}
