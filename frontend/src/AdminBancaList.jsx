import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const TIPO_LABEL = {
    1: 'Mestrado',
    2: 'Qualificação',
    3: 'Doutorado',
}

const STATUS_LABEL = {
    pending: 'Pendente',
    approved: 'Aceita',
    rejected: 'Recusada',
}

function formatDate(iso) {
    if (!iso) return '—'
    const [y, m, d] = iso.split('-')
    return `${d}/${m}/${y}`
}

export default function AdminBancaList() {
    const navigate = useNavigate()
    const [filters, setFilters] = useState({ status: '', ata: '', student: '', orientador: '', q: '' })
    const [items, setItems] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        let cancelled = false
        const handle = setTimeout(() => {
            const params = new URLSearchParams()
            if (filters.status) params.set('status', filters.status)
            if (filters.ata) params.set('ata', filters.ata)
            if (filters.student) params.set('student', filters.student)
            if (filters.orientador) params.set('orientador', filters.orientador)
            if (filters.q) params.set('q', filters.q)
            const qs = params.toString()
            const url = qs ? `/admin/bancas?${qs}` : '/admin/bancas'

            setLoading(true)
            setError(null)
            fetch(url)
                .then(async res => {
                    const data = await res.json()
                    if (cancelled) return
                    if (res.ok) {
                        setItems(data)
                    } else {
                        setError(typeof data.detail === 'string' ? data.detail : 'Erro ao listar bancas.')
                    }
                })
                .catch(err => {
                    if (!cancelled) setError('Erro de conexão: ' + err.message)
                })
                .finally(() => {
                    if (!cancelled) setLoading(false)
                })
        }, 250)

        return () => {
            cancelled = true
            clearTimeout(handle)
        }
    }, [filters.status, filters.ata, filters.student, filters.orientador, filters.q])

    function setF(field, value) {
        setFilters(f => ({ ...f, [field]: value }))
    }

    return (
        <div className="container">
            <h1>SigBah! — Administração de Bancas</h1>

            <section>
                <h2>Filtros</h2>
                <div className="row">
                    <label>
                        Status
                        <select value={filters.status} onChange={e => setF('status', e.target.value)}>
                            <option value="">Todos</option>
                            <option value="pending">Pendente</option>
                            <option value="approved">Aceita</option>
                            <option value="rejected">Recusada</option>
                        </select>
                    </label>
                    <label>
                        Ata
                        <input type="number" min={1} value={filters.ata} onChange={e => setF('ata', e.target.value)} />
                    </label>
                    <label>
                        Aluno(a)
                        <input type="text" value={filters.student} onChange={e => setF('student', e.target.value)} />
                    </label>
                    <label>
                        Orientador(a)
                        <input type="text" value={filters.orientador} onChange={e => setF('orientador', e.target.value)} />
                    </label>
                </div>
                <label>
                    Busca livre
                    <input
                        type="text"
                        value={filters.q}
                        onChange={e => setF('q', e.target.value)}
                        placeholder="Nome, orientador, título…"
                    />
                </label>
            </section>

            {error && <div className="alert alert-err">{error}</div>}

            <section>
                <h2>Resultados {loading ? '(carregando…)' : `(${items.length})`}</h2>
                {items.length === 0 && !loading && !error && (
                    <p style={{ color: '#6b7280' }}>Nenhuma banca encontrada.</p>
                )}
                {items.length > 0 && (
                    <table className="banca-table">
                        <thead>
                            <tr>
                                <th>Ata</th>
                                <th>Aluno(a)</th>
                                <th>Tipo</th>
                                <th>Data</th>
                                <th>Orientador(a)</th>
                                <th>Status</th>
                                <th>Versão</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {items.map(it => (
                                <tr key={it.decision_token}>
                                    <td>{it.ata}</td>
                                    <td>{it.student_name}</td>
                                    <td>{TIPO_LABEL[it.tipo] || it.tipo}</td>
                                    <td>{formatDate(it.data)}</td>
                                    <td>{it.orientador_name}</td>
                                    <td>{STATUS_LABEL[it.status] || it.status}</td>
                                    <td>v{it.current_version}</td>
                                    <td>
                                        <button
                                            type="button"
                                            className="open-btn"
                                            onClick={() => navigate(`/admin/banca/${it.decision_token}`)}
                                        >
                                            Abrir
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </section>
        </div>
    )
}
