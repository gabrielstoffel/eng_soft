import { useFormContext } from 'react-hook-form'

import { emptyMemberForm, type NewBancaFormState } from '../../types/new-banca.ts'
import type { MemberRole, OptionalMemberRole } from './config'

type MemberFieldProps = {
  label: string
  name: MemberRole
  required?: boolean
  requireEmail?: boolean
  disabled?: boolean
}

export default function MemberField({
  label,
  name,
  required = false,
  requireEmail = false,
  disabled = false,
}: MemberFieldProps) {
  const { register, setValue, watch } = useFormContext<NewBancaFormState>()
  const value = watch(name)
  const enabled = required || value !== null

  function parseGender(raw: string): 0 | 1 {
    return raw === '1' ? 1 : 0
  }

  function toggle(checked: boolean) {
    if (required) return
    setValue(name as OptionalMemberRole, checked ? { ...emptyMemberForm } : null)
  }

  return (
    <fieldset>
      <legend>
        {!required && (
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => toggle(e.target.checked)}
            disabled={disabled}
            style={{ marginRight: 6 }}
          />
        )}
        {label}
      </legend>

      {enabled && value && (
        <div className="member-grid">
          <label>
            Tratamento *
            <select
              required
              disabled={disabled}
              {...register(`${name}.gender`, {
                setValueAs: (fieldValue) => parseGender(String(fieldValue)),
              })}
            >
              <option value={0}>Prof. Dr.</option>
              <option value={1}>Profª. Drª.</option>
            </select>
          </label>

          <label>
            Nome *
            <input
              type="text"
              required
              disabled={disabled}
              {...register(`${name}.name`)}
            />
          </label>

          <label>
            Instituição *
            <input
              type="text"
              required
              disabled={disabled}
              {...register(`${name}.institution`)}
            />
          </label>

          <label>
            Localidade *
            <input
              type="text"
              required
              disabled={disabled}
              {...register(`${name}.location`)}
            />
          </label>

          <label>
            Idioma da carta *
            <select
              required
              disabled={disabled}
              {...register(`${name}.lang`)}
            >
              <option value="pt">Português</option>
              <option value="en">English</option>
            </select>
          </label>

          <label>
            E-mail{requireEmail ? ' *' : ''}
            <input
              type="email"
              required={requireEmail}
              disabled={disabled}
              placeholder="email@instituicao.br"
              {...register(`${name}.email`)}
            />
          </label>
        </div>
      )}
    </fieldset>
  )
}
