import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import BancaForm, { deserializeBanca, serializeBanca } from './pages/NewBanca/form/BancaForm'

const STATUS_LABEL = {
    pending: 'Pendente',
    approved: 'Aceita',
    rejected: 'Recusada',
}

function formatTimestamp(iso) {
    if (!iso) return '—'
    const d = new Date(iso)
    if (isNaN(d.getTime())) return iso
    return d.toLocaleString('pt-BR')
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
}

function filenameFromContentDisposition(header) {
    if (!header) return null
    const utf8 = header.match(/filename\*=UTF-8''([^;]+)/i)
    if (utf8) {
        try {
            return decodeURIComponent(utf8[1])
        } catch {
            // fall through
        }
    }
    const match = header.match(/filename="?([^";]+)"?/i)
    return match ? match[1] : null
}

export default function AdminBancaDetail() {
    const { token } = useParams()
    const [detail, setDetail] = useState(null)
    const [loadError, setLoadError] = useState(null)
    const [loading, setLoading] = useState(true)

    const [selectedVersion, setSelectedVersion] = useState(null)
    const [editing, setEditing] = useState(false)
    const [editForm, setEditForm] = useState(null)
    const [saveStatus, setSaveStatus] = useState(null)
    const [saving, setSaving] = useState(false)

    const [regenVersion, setRegenVersion] = useState(null)
    const [files, setFiles] = useState([])
    const [filesError, setFilesError] = useState(null)
    const [filesLoading, setFilesLoading] = useState(false)
    const [selectedIds, setSelectedIds] = useState(new Set())
    const [downloadStatus, setDownloadStatus] = useState(null)
    const [downloadInFlight, setDownloadInFlight] = useState(null) // null | 'bulk' | <id>

    useEffect(() => {
        let cancelled = false
        async function load() {
            setLoading(true)
            try {
                const res = await fetch(`/admin/bancas/${token}`)
                const data = await res.json()
                if (cancelled) return
                if (res.ok) {
                    setDetail(data)
                    setSelectedVersion(data.current_version)
                    setRegenVersion(data.current_version)
                } else {
                    setLoadError(typeof data.detail === 'string' ? data.detail : 'Erro ao carregar banca.')
                }
            } catch (err) {
                if (!cancelled) setLoadError('Erro de conexão: ' + err.message)
            } finally {
                if (!cancelled) setLoading(false)
            }
        }
        load()
        return () => { cancelled = true }
    }, [token])

    useEffect(() => {
        if (regenVersion == null) return
        let cancelled = false
        setFilesLoading(true)
        setFilesError(null)
        fetch(`/admin/bancas/${token}/files?version=${regenVersion}`)
            .then(async res => {
                const data = await res.json()
                if (cancelled) return
                if (res.ok) {
                    setFiles(data)
                    setSelectedIds(new Set())
                } else {
                    setFilesError(typeof data.detail === 'string' ? data.detail : 'Erro ao listar arquivos.')
                }
            })
            .catch(err => {
                if (!cancelled) setFilesError('Erro de conexão: ' + err.message)
            })
            .finally(() => {
                if (!cancelled) setFilesLoading(false)
            })
        return () => { cancelled = true }
    }, [token, regenVersion])

    if (loading) {
        return <div className="container"><p>Carregando…</p></div>
    }
    if (loadError) {
        return (
            <div className="container">
                <h1>SigBah! — Detalhes da Banca</h1>
                <div className="alert alert-err">{loadError}</div>
                <p><Link to="/admin">← Voltar à lista</Link></p>
            </div>
        )
    }

    const versionEntry = detail.versions.find(v => v.version === selectedVersion) || detail.versions[detail.versions.length - 1]
    const req = versionEntry.request
    const isApproved = detail.status === 'approved'
    const isLatest = selectedVersion === detail.current_version
    const canEdit = isApproved && isLatest
    const editTooltip = !isApproved
        ? 'Edição disponível apenas para bancas aceitas.'
        : !isLatest
            ? 'Edite somente a versão atual; a edição cria uma nova versão.'
            : ''

    function startEdit() {
        setEditForm(deserializeBanca(req))
        setEditing(true)
        setSaveStatus(null)
    }

    function cancelEdit() {
        setEditing(false)
        setEditForm(null)
        setSaveStatus(null)
    }

    async function saveEdit(e) {
        e.preventDefault()
        setSaving(true)
        setSaveStatus(null)
        try {
            const body = serializeBanca(editForm)
            const res = await fetch(`/admin/bancas/${token}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            })
            const data = await res.json()
            if (res.ok) {
                if (data.created_new_version) {
                    setSaveStatus({ ok: true, message: `Nova versão criada (v${data.current_version}).` })
                } else {
                    setSaveStatus({ ok: true, message: 'Sem alterações detectadas; nenhuma nova versão criada.' })
                }
                const refetch = await fetch(`/admin/bancas/${token}`)
                const refreshed = await refetch.json()
                if (refetch.ok) {
                    setDetail(refreshed)
                    setSelectedVersion(refreshed.current_version)
                    setRegenVersion(refreshed.current_version)
                }
                setEditing(false)
                setEditForm(null)
            } else {
                let msg
                if (res.status === 409 && data.detail && typeof data.detail === 'object') {
                    msg = data.detail.message || 'Banca não pode ser editada.'
                } else if (Array.isArray(data.detail)) {
                    msg = data.detail.map(d => d.msg + ' (' + d.loc.join('.') + ')').join('; ')
                } else {
                    msg = data.detail || 'Erro inesperado.'
                }
                setSaveStatus({ ok: false, message: msg })
            }
        } catch (err) {
            setSaveStatus({ ok: false, message: 'Erro de conexão: ' + err.message })
        } finally {
            setSaving(false)
        }
    }

    function toggleSelect(id) {
        setSelectedIds(prev => {
            const next = new Set(prev)
            if (next.has(id)) next.delete(id)
            else next.add(id)
            return next
        })
    }

    function toggleSelectAll() {
        if (selectedIds.size === files.length) {
            setSelectedIds(new Set())
        } else {
            setSelectedIds(new Set(files.map(f => f.id)))
        }
    }

    async function downloadIds(ids, inFlightTag) {
        if (ids.length === 0) return
        setDownloadInFlight(inFlightTag)
        setDownloadStatus(null)
        try {
            const params = new URLSearchParams()
            params.set('version', regenVersion)
            for (const id of ids) params.append('id', id)
            const res = await fetch(`/admin/bancas/${token}/files/download?${params.toString()}`)
            if (!res.ok) {
                let msg
                try {
                    const data = await res.json()
                    msg = typeof data.detail === 'string' ? data.detail : (data.detail?.message || 'Erro ao gerar documento.')
                } catch {
                    msg = `Erro ao gerar documento (${res.status}).`
                }
                setDownloadStatus({ ok: false, message: msg })
                return
            }
            const blob = await res.blob()
            const filename = filenameFromContentDisposition(res.headers.get('Content-Disposition'))
                || (ids.length === 1 ? `${ids[0]}.pdf` : `bancas_${token}.zip`)
            downloadBlob(blob, filename)
            setDownloadStatus({ ok: true, message: `Baixado: ${filename}` })
        } catch (err) {
            setDownloadStatus({ ok: false, message: 'Erro de conexão: ' + err.message })
        } finally {
            setDownloadInFlight(null)
        }
    }

    return (
        <div className="container">
            <h1>SigBah! — Detalhes da Banca</h1>
            <p><Link to="/admin">← Voltar à lista</Link></p>

            <section>
                <h2>Status</h2>
                <div className="row">
                    <label>
                        Status atual
                        <input type="text" value={STATUS_LABEL[detail.status] || detail.status} readOnly />
                    </label>
                    <label>
                        Versão atual
                        <input type="text" value={`v${detail.current_version}`} readOnly />
                    </label>
                    <label>
                        Criada em
                        <input type="text" value={formatTimestamp(detail.created_at)} readOnly />
                    </label>
                    <label>
                        Decidida em
                        <input type="text" value={formatTimestamp(detail.decided_at)} readOnly />
                    </label>
                </div>
                {detail.rejection_reason && (
                    <label>
                        Razão da recusa
                        <textarea value={detail.rejection_reason} readOnly rows={3} />
                    </label>
                )}
            </section>

            <section>
                <h2>Versão</h2>
                <div className="row">
                    <label>
                        Visualizar versão
                        <select
                            value={selectedVersion}
                            disabled={editing}
                            onChange={e => setSelectedVersion(Number(e.target.value))}
                        >
                            {detail.versions.map(v => (
                                <option key={v.version} value={v.version}>
                                    v{v.version} — {formatTimestamp(v.created_at)}
                                    {v.version === detail.current_version ? ' (atual)' : ''}
                                </option>
                            ))}
                        </select>
                    </label>
                </div>
            </section>

            {editing ? (
                <form onSubmit={saveEdit}>
                    <BancaForm value={editForm} onChange={setEditForm} />
                    {saveStatus && (
                        <div className={saveStatus.ok ? 'alert alert-ok' : 'alert alert-err'}>
                            {saveStatus.message}
                        </div>
                    )}
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <button
                            type="button"
                            onClick={cancelEdit}
                            disabled={saving}
                            style={{
                                flex: 1, padding: '0.7rem 2rem', background: '#6b7280', color: '#fff',
                                border: 'none', borderRadius: 4, fontSize: '1rem', cursor: 'pointer',
                            }}
                        >
                            Cancelar
                        </button>
                        <button type="submit" disabled={saving}>
                            {saving ? 'Salvando…' : 'Salvar (cria nova versão)'}
                        </button>
                    </div>
                </form>
            ) : (
                <>
                    <BancaForm value={deserializeBanca(req)} onChange={() => {}} disabled />
                    {saveStatus && (
                        <div className={saveStatus.ok ? 'alert alert-ok' : 'alert alert-err'}>
                            {saveStatus.message}
                        </div>
                    )}
                    <div style={{ display: 'flex', gap: '0.75rem' }} title={editTooltip}>
                        <button
                            type="button"
                            onClick={startEdit}
                            disabled={!canEdit}
                            style={{
                                flex: 1, padding: '0.7rem 2rem',
                                background: canEdit ? '#3b82f6' : '#9ca3af',
                                color: '#fff', border: 'none', borderRadius: 4,
                                fontSize: '1rem', cursor: canEdit ? 'pointer' : 'not-allowed',
                            }}
                        >
                            Editar
                        </button>
                    </div>
                    {!canEdit && editTooltip && (
                        <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>{editTooltip}</p>
                    )}
                </>
            )}

            <section>
                <h2>Documentos</h2>
                <div className="row">
                    <label>
                        Versão de origem
                        <select
                            value={regenVersion ?? ''}
                            onChange={e => setRegenVersion(Number(e.target.value))}
                        >
                            {detail.versions.map(v => (
                                <option key={v.version} value={v.version}>
                                    v{v.version} — {formatTimestamp(v.created_at)}
                                </option>
                            ))}
                        </select>
                    </label>
                </div>

                {filesError && <div className="alert alert-err">{filesError}</div>}

                {filesLoading && <p style={{ color: '#6b7280' }}>Carregando lista de arquivos…</p>}

                {!filesLoading && files.length > 0 && (
                    <>
                        <table className="banca-table">
                            <thead>
                                <tr>
                                    <th style={{ width: '2rem' }}>
                                        <input
                                            type="checkbox"
                                            checked={selectedIds.size === files.length}
                                            onChange={toggleSelectAll}
                                            aria-label="Selecionar todos"
                                        />
                                    </th>
                                    <th>Arquivo</th>
                                    <th style={{ width: '8rem' }}></th>
                                </tr>
                            </thead>
                            <tbody>
                                {files.map(f => {
                                    const inFlight = downloadInFlight === f.id
                                    return (
                                        <tr key={f.id}>
                                            <td>
                                                <input
                                                    type="checkbox"
                                                    checked={selectedIds.has(f.id)}
                                                    onChange={() => toggleSelect(f.id)}
                                                />
                                            </td>
                                            <td>{f.label}</td>
                                            <td>
                                                <button
                                                    type="button"
                                                    onClick={() => downloadIds([f.id], f.id)}
                                                    disabled={!!downloadInFlight}
                                                    style={{
                                                        padding: '0.35rem 0.75rem',
                                                        background: '#1f2937', color: '#fff',
                                                        border: 'none', borderRadius: 4,
                                                        fontSize: '0.85rem',
                                                        cursor: downloadInFlight ? 'not-allowed' : 'pointer',
                                                        opacity: downloadInFlight && !inFlight ? 0.5 : 1,
                                                    }}
                                                >
                                                    {inFlight ? 'Gerando…' : 'Baixar'}
                                                </button>
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>

                        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
                            <button
                                type="button"
                                onClick={() => downloadIds([...selectedIds], 'bulk')}
                                disabled={selectedIds.size === 0 || !!downloadInFlight}
                                style={{
                                    padding: '0.6rem 1.5rem',
                                    background: selectedIds.size === 0 ? '#9ca3af' : '#3b82f6',
                                    color: '#fff', border: 'none', borderRadius: 4,
                                    fontSize: '0.95rem',
                                    cursor: (selectedIds.size === 0 || downloadInFlight) ? 'not-allowed' : 'pointer',
                                }}
                            >
                                {downloadInFlight === 'bulk'
                                    ? 'Gerando…'
                                    : `Baixar selecionados (${selectedIds.size})`}
                            </button>
                        </div>
                    </>
                )}

                {!filesLoading && files.length === 0 && !filesError && (
                    <p style={{ color: '#6b7280' }}>Nenhum arquivo disponível para esta versão.</p>
                )}

                {downloadStatus && (
                    <div className={downloadStatus.ok ? 'alert alert-ok' : 'alert alert-err'}>
                        {downloadStatus.message}
                    </div>
                )}
            </section>
        </div>
    )
}
