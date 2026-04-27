const EMPTY_MEMBER = { gender: 0, name: '', institution: '', location: '', lang: 'pt', email: '' }

export default function MemberField({ label, value, onChange, required = false, requireEmail = false }) {
  const enabled = required || value !== null

  function toggle(e) {
    onChange(e.target.checked ? { ...EMPTY_MEMBER } : null)
  }

  function update(field, val) {
    onChange({ ...value, [field]: val })
  }

  return (
    <fieldset>
      <legend>
        {!required && (
          <input type="checkbox" checked={enabled} onChange={toggle} style={{ marginRight: 6 }} />
        )}
        {label}
      </legend>

      {enabled && (
        <div className="member-grid">
          <label>
            Tratamento
            <select value={value.gender} onChange={e => update('gender', Number(e.target.value))}>
              <option value={0}>Prof. Dr.</option>
              <option value={1}>Profª. Drª.</option>
            </select>
          </label>

          <label>
            Nome
            <input
              type="text"
              required
              value={value.name}
              onChange={e => update('name', e.target.value)}
            />
          </label>

          <label>
            Instituição
            <input
              type="text"
              required
              value={value.institution}
              onChange={e => update('institution', e.target.value)}
            />
          </label>

          <label>
            Localidade
            <input
              type="text"
              required
              value={value.location}
              onChange={e => update('location', e.target.value)}
            />
          </label>

          <label>
            Idioma da carta
            <select value={value.lang} onChange={e => update('lang', e.target.value)}>
              <option value="pt">Português</option>
              <option value="en">English</option>
            </select>
          </label>

          <label>
            E-mail{requireEmail ? ' *' : ''}
            <input
              type="email"
              required={requireEmail}
              value={value.email ?? ''}
              onChange={e => update('email', e.target.value)}
              placeholder="email@instituicao.br"
            />
          </label>
        </div>
      )}
    </fieldset>
  )
}
