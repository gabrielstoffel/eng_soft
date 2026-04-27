import { useState } from 'react'
import MemberField from './MemberField.jsx'
import { isDevelopment } from './env.js'

const EMPTY_MEMBER = { gender: 0, name: '', institution: '', location: '', lang: 'pt', email: '' }

const ALL_ROLES = ['orientador', 'coorientador', 'externo1', 'externo2', 'interno1', 'interno2', 'supl_int', 'supl_ext']

// Field visibility per banca tipo. 'required' = always shown, no toggle. 'optional' = shown with checkbox.
// 'hidden' = not shown and submitted as null.
const ROLES_BY_TIPO = {
    1: { // Mestrado
        orientador: 'required',
        coorientador: 'optional',
        externo1: 'required',
        externo2: 'optional',
        interno1: 'required',
        interno2: 'optional',
        supl_int: 'optional',
        supl_ext: 'optional',
    },
    2: { // Exame de Qualificação ao Doutorado
        orientador: 'required',
        coorientador: 'optional',
        externo1: 'hidden',
        externo2: 'hidden',
        interno1: 'required',
        interno2: 'required',
        supl_int: 'optional',
        supl_ext: 'hidden',
    },
    3: { // Doutorado
        orientador: 'required',
        coorientador: 'optional',
        externo1: 'required',
        externo2: 'required',
        interno1: 'required',
        interno2: 'optional',
        supl_int: 'optional',
        supl_ext: 'optional',
    },
}

const ROLE_LABELS = {
    orientador: 'Orientador(a)',
    coorientador: 'Coorientador(a)',
    externo1: 'Externo 1',
    externo2: 'Externo 2',
    interno1: 'Interno 1',
    interno2: 'Interno 2',
    supl_int: 'Suplente Interno',
    supl_ext: 'Suplente Externo',
}

const INITIAL = {
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

const MOCK = {
    nome: { gender: 0, name: 'João da Silva' },
    tipo: 1,
    data: '2026-06-12',
    horario: '14:00',
    data_convite: '2026-05-20',
    ata: 420,
    local_banca: 'Sala 220 — Instituto de Física',
    link: 'https://meet.example.com/banca-mock',
    titulo: 'Estudo sobre filas de espera em sistemas distribuídos',
    titulo2: 'A study on waiting queues in distributed systems',
    orientador: { gender: 0, name: 'Carlos Oliveira', institution: 'UFRGS', location: 'Porto Alegre, RS', lang: 'pt', email: 'orientador@ufrgs.br' },
    coorientador: { gender: 1, name: 'Beatriz Lima', institution: 'UFRGS', location: 'Porto Alegre, RS', lang: 'pt', email: 'beatriz.lima@ufrgs.br' },
    externo1: { gender: 1, name: 'Ana Costa', institution: 'USP', location: 'São Paulo, SP', lang: 'pt', email: 'ana.costa@usp.br' },
    externo2: { gender: 0, name: 'Rafael Mendes', institution: 'UNICAMP', location: 'Campinas, SP', lang: 'pt', email: 'rafael.mendes@unicamp.br' },
    interno1: { gender: 0, name: 'Pedro Santos', institution: 'UFRGS', location: 'Porto Alegre, RS', lang: 'pt', email: 'pedro.santos@ufrgs.br' },
    interno2: { gender: 1, name: 'Marina Souza', institution: 'UFRGS', location: 'Porto Alegre, RS', lang: 'pt', email: 'marina.souza@ufrgs.br' },
    supl_int: { gender: 0, name: 'Lucas Almeida', institution: 'UFRGS', location: 'Porto Alegre, RS', lang: 'pt', email: 'lucas.almeida@ufrgs.br' },
    supl_ext: { gender: 1, name: 'Carla Ferreira', institution: 'UFSC', location: 'Florianópolis, SC', lang: 'pt', email: 'carla.ferreira@ufsc.br' },
}

const INITIAL_FORM = isDevelopment ? MOCK : INITIAL

function coerceMember(m) {
    if (!m) return null
    return { ...m, gender: Number(m.gender), email: m.email || null }
}

export default function PetitionForm() {
    const [form, setForm] = useState(INITIAL_FORM)
    const [status, setStatus] = useState(null) // { ok: bool, message: string }
    const [loading, setLoading] = useState(false)

    function set(field, value) {
        setForm(f => ({ ...f, [field]: value }))
    }

    function changeTipo(newTipo) {
        const newRoles = ROLES_BY_TIPO[newTipo]
        setForm(f => {
            const next = { ...f, tipo: newTipo }
            for (const role of ALL_ROLES) {
                if (newRoles[role] === 'required' && !f[role]) {
                    next[role] = { ...EMPTY_MEMBER }
                }
            }
            return next
        })
    }

    async function handleSubmit(e) {
        e.preventDefault()
        setLoading(true)
        setStatus(null)

        const tipo = Number(form.tipo)
        const roles = ROLES_BY_TIPO[tipo]
        const memberPayload = {}
        for (const role of ALL_ROLES) {
            memberPayload[role] = roles[role] === 'hidden' ? null : coerceMember(form[role])
        }

        const body = {
            ...form,
            tipo,
            ata: Number(form.ata),
            nome: { ...form.nome, gender: Number(form.nome.gender) },
            data_convite: form.data_convite || null,
            local_banca: form.local_banca || null,
            link: form.link || null,
            ...memberPayload,
        }

        try {
            const res = await fetch('/banca', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            })
            const data = await res.json()
            if (res.ok) {
                setStatus({
                    ok: true,
                    message: `Pedido enviado ao coordenador. (Banca #${data.ata} — ${data.student_name})`,
                })
                setForm(INITIAL_FORM)
            } else {
                const detail = Array.isArray(data.detail)
                    ? data.detail.map(d => d.msg + ' (' + d.loc.join('.') + ')').join('; ')
                    : data.detail
                setStatus({ ok: false, message: detail })
            }
        } catch (err) {
            setStatus({ ok: false, message: 'Erro de conexão: ' + err.message })
        } finally {
            setLoading(false)
        }
    }

    const visibleRoles = ROLES_BY_TIPO[Number(form.tipo)]

    return (
        <div className="container">
            <h1>SigBah! — Nova Banca</h1>

            <form onSubmit={handleSubmit}>
                <section>
                    <h2>Dados Gerais</h2>

                    <div className="row">
                        <label>
                            Tratamento do(a) aluno(a)
                            <select value={form.nome.gender} onChange={e => set('nome', { ...form.nome, gender: e.target.value })}>
                                <option value={0}>Masculino</option>
                                <option value={1}>Feminino</option>
                            </select>
                        </label>

                        <label>
                            Nome do(a) aluno(a) *
                            <input
                                type="text"
                                required
                                value={form.nome.name}
                                onChange={e => set('nome', { ...form.nome, name: e.target.value })}
                            />
                        </label>
                    </div>

                    <div className="row">
                        <label>
                            Tipo *
                            <select value={form.tipo} onChange={e => changeTipo(Number(e.target.value))}>
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
                                value={form.ata}
                                onChange={e => set('ata', e.target.value)}
                            />
                        </label>
                    </div>

                    <div className="row">
                        <label>
                            Data da defesa *
                            <input type="date" required value={form.data} onChange={e => set('data', e.target.value)} />
                        </label>

                        <label>
                            Horário *
                            <input type="time" required value={form.horario} onChange={e => set('horario', e.target.value)} />
                        </label>

                        <label>
                            Data dos convites
                            <input type="date" value={form.data_convite} onChange={e => set('data_convite', e.target.value)} />
                        </label>
                    </div>

                    <div className="row">
                        <label>
                            Local
                            <input type="text" value={form.local_banca} onChange={e => set('local_banca', e.target.value)} />
                        </label>

                        <label>
                            Link (videoconferência)
                            <input type="url" value={form.link} onChange={e => set('link', e.target.value)} />
                        </label>
                    </div>

                    <label>
                        Título (PT) *
                        <input type="text" required value={form.titulo} onChange={e => set('titulo', e.target.value)} />
                    </label>

                    <label>
                        Title (EN) *
                        <input type="text" required value={form.titulo2} onChange={e => set('titulo2', e.target.value)} />
                    </label>
                </section>

                <section>
                    <h2>Membros da Banca</h2>

                    {ALL_ROLES.map(role => {
                        const visibility = visibleRoles[role]
                        if (visibility === 'hidden') return null
                        const required = visibility === 'required'
                        const star = required ? ' *' : ''
                        return (
                            <MemberField
                                key={role}
                                label={`${ROLE_LABELS[role]}${star}`}
                                value={form[role]}
                                onChange={v => set(role, v)}
                                required={required}
                                requireEmail={role === 'orientador'}
                            />
                        )
                    })}
                </section>

                {status && (
                    <div className={status.ok ? 'alert alert-ok' : 'alert alert-err'}>
                        {status.message}
                    </div>
                )}

                <button type="submit" disabled={loading}>
                    {loading ? 'Enviando...' : 'Enviar Pedido ao Coordenador'}
                </button>
            </form>
        </div>
    )
}
