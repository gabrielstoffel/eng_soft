import MemberField from '../../MemberField.jsx'

export const EMPTY_MEMBER = { gender: 0, name: '', institution: '', location: '', lang: 'pt', email: '' }

export const ALL_ROLES = ['orientador', 'coorientador', 'externo1', 'externo2', 'interno1', 'interno2', 'supl_int', 'supl_ext']

export const ROLES_BY_TIPO = {
    1: { // Mestrado
        orientador: 'required',
        coorientador: 'optional',
        externo1: 'required',
        externo2: 'hidden',
        interno1: 'required',
        interno2: 'required',
        supl_int: 'optional',
        supl_ext: 'optional',
    },
    2: { // Exame de Qualificação ao Doutorado
        orientador: 'required',
        coorientador: 'optional',
        externo1: 'required',
        externo2: 'optional',
        interno1: 'required',
        interno2: 'required',
        supl_int: 'optional',
        supl_ext: 'optional',
    },
    3: { // Doutorado
        orientador: 'required',
        coorientador: 'optional',
        externo1: 'required',
        externo2: 'required',
        interno1: 'required',
        interno2: 'required',
        supl_int: 'optional',
        supl_ext: 'optional',
    },
}

export const ROLE_LABELS = {
    orientador: 'Orientador(a)',
    coorientador: 'Coorientador(a)',
    externo1: 'Externo 1',
    externo2: 'Externo 2',
    interno1: 'Interno 1',
    interno2: 'Interno 2',
    supl_int: 'Suplente Interno',
    supl_ext: 'Suplente Externo',
}

export const INITIAL_FORM = {
    nome: { gender: 0, name: '' },
    tipo: 1,
    data: '',
    horario: '',
    data_convite: '',
    ata: '',
    local_banca: '',
    link: '',
    titulo: '',
    titulo2: '',
    orientador: { ...EMPTY_MEMBER },
    coorientador: null,
    externo1: { ...EMPTY_MEMBER },
    externo2: null,
    interno1: { ...EMPTY_MEMBER },
    interno2: { ...EMPTY_MEMBER },
    supl_int: null,
    supl_ext: null,
}

function coerceMember(m) {
    if (!m) return null
    return { ...m, gender: Number(m.gender), email: m.email || null }
}

export function serializeBanca(form) {
    const tipo = Number(form.tipo)
    const roles = ROLES_BY_TIPO[tipo]
    const memberPayload = {}
    for (const role of ALL_ROLES) {
        memberPayload[role] = roles[role] === 'hidden' ? null : coerceMember(form[role])
    }
    return {
        ...form,
        tipo,
        ata: Number(form.ata),
        nome: { ...form.nome, gender: Number(form.nome.gender) },
        data_convite: form.data_convite || null,
        local_banca: form.local_banca || null,
        link: form.link || null,
        ...memberPayload,
    }
}

// Convert a backend BancaRequest payload into the form-friendly shape used by INITIAL_FORM
// (date/time strings as plain strings, missing optional members rendered as null).
export function deserializeBanca(req) {
    const fillMember = (m) => (m ? { ...EMPTY_MEMBER, ...m, email: m.email ?? '' } : null)
    return {
        nome: { gender: req.nome.gender, name: req.nome.name },
        tipo: req.tipo,
        data: req.data || '',
        horario: req.horario || '',
        data_convite: req.data_convite || '',
        ata: req.ata,
        local_banca: req.local_banca || '',
        link: req.link || '',
        titulo: req.titulo,
        titulo2: req.titulo2,
        orientador: fillMember(req.orientador),
        coorientador: fillMember(req.coorientador),
        externo1: fillMember(req.externo1),
        externo2: fillMember(req.externo2),
        interno1: fillMember(req.interno1),
        interno2: fillMember(req.interno2),
        supl_int: fillMember(req.supl_int),
        supl_ext: fillMember(req.supl_ext),
    }
}

export default function BancaForm({ value, onChange, disabled = false }) {
    const form = value

    function set(field, v) {
        onChange({ ...form, [field]: v })
    }

    function changeTipo(newTipo) {
        const newRoles = ROLES_BY_TIPO[newTipo]
        const next = { ...form, tipo: newTipo }
        for (const role of ALL_ROLES) {
            if (newRoles[role] === 'required' && !form[role]) {
                next[role] = { ...EMPTY_MEMBER }
            }
        }
        onChange(next)
    }

    const visibleRoles = ROLES_BY_TIPO[Number(form.tipo)]

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
                            onChange={e => set('nome', { ...form.nome, gender: e.target.value })}
                        >
                            <option value={0}>Masculino</option>
                            <option value={1}>Feminino</option>
                        </select>
                    </label>

                    <label>
                        Nome do(a) aluno(a) *
                        <input
                            type="text"
                            required
                            disabled={disabled}
                            value={form.nome.name}
                            onChange={e => set('nome', { ...form.nome, name: e.target.value })}
                        />
                    </label>
                </div>

                <div className="row">
                    <label>
                        Tipo *
                        <select
                            value={form.tipo}
                            disabled={disabled}
                            onChange={e => changeTipo(Number(e.target.value))}
                        >
                            <option value={1}>Dissertação de Mestrado</option>
                            <option value={2}>Exame de Qualificação ao Doutorado</option>
                            <option value={3}>Tese de Doutorado</option>
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
                            onChange={e => set('ata', e.target.value)}
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
                            onChange={e => set('data', e.target.value)}
                        />
                    </label>

                    <label>
                        Horário *
                        <input
                            type="time"
                            required
                            disabled={disabled}
                            value={form.horario}
                            onChange={e => set('horario', e.target.value)}
                        />
                    </label>

                    <label>
                        Data dos convites
                        <input
                            type="date"
                            disabled={disabled}
                            value={form.data_convite}
                            onChange={e => set('data_convite', e.target.value)}
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
                            onChange={e => set('local_banca', e.target.value)}
                        />
                    </label>

                    <label>
                        Link (videoconferência)
                        <input
                            type="url"
                            disabled={disabled}
                            value={form.link}
                            onChange={e => set('link', e.target.value)}
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
                        onChange={e => set('titulo', e.target.value)}
                    />
                </label>

                <label>
                    Título (EN) *
                    <input
                        type="text"
                        required
                        disabled={disabled}
                        value={form.titulo2}
                        onChange={e => set('titulo2', e.target.value)}
                    />
                </label>
            </section>

            <section>
                <h2>Composição da Banca</h2>

                {Object.entries(visibleRoles).map(([role, mode]) =>
                    mode === 'hidden' ? null : (
                        <MemberField
                            key={role}
                            label={ROLE_LABELS[role]}
                            value={form[role]}
                            onChange={v => set(role, v)}
                            required={mode === 'required'}
                            requireEmail={role === 'orientador' || role.startsWith('externo') || role.startsWith('supl_')}
                            disabled={disabled}
                        />
                    )
                )}
            </section>
        </>
    )
}
