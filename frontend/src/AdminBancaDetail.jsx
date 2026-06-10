import { useEffect, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { Link, useParams } from 'react-router-dom'
import { newBancaDefaultValues } from './types/new-banca.ts'
import { deserializeBanca, serializeBanca } from './pages/NewBanca/form/BancaForm'
import BancaGeneralSection from './pages/NewBanca/form/BancaGeneralSection'
import BancaCompositionSection from './pages/NewBanca/form/BancaCompositionSection'

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
    const [saveStatus, setSaveStatus] = useState(null)
    const [saving, setSaving] = useState(false)

    const [regenVersion, setRegenVersion] = useState(null)
    const [files, setFiles] = useState([])
    const [filesError, setFilesError] = useState(null)
    const [filesLoading, setFilesLoading] = useState(false)
    const [selectedIds, setSelectedIds] = useState(new Set())
    const [downloadStatus, setDownloadStatus] = useState(null)
    const [downloadInFlight, setDownloadInFlight] = useState(null) // null | 'bulk' | <id>

    const [invites, setInvites] = useState([])
    const [invitesError, setInvitesError] = useState(null)
    const [invitesLoading, setInvitesLoading] = useState(false)
    const [sendInFlight, setSendInFlight] = useState(null) // null | 'convites' | 'pareceres' | <item_id>
    const [sendStatus, setSendStatus] = useState(null)

    const previewForm = useForm({ defaultValues: newBancaDefaultValues })
    const editMethods = useForm({ defaultValues: newBancaDefaultValues })

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

    useEffect(() => {
        if (!detail) return
        let cancelled = false
        setInvitesLoading(true)
        setInvitesError(null)
        fetch(`/admin/bancas/${token}/invites`)
            .then(async res => {
                const data = await res.json()
                if (cancelled) return
                if (res.ok) setInvites(data)
                else setInvitesError(typeof data.detail === 'string' ? data.detail : 'Erro ao listar convites.')
            })
            .catch(err => { if (!cancelled) setInvitesError('Erro de conexão: ' + err.message) })
            .finally(() => { if (!cancelled) setInvitesLoading(false) })
        return () => { cancelled = true }
        // member emails can change when a new version is created, so refetch on
        // status/version change rather than on every `detail` object identity.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [token, detail?.status, detail?.current_version])

    const versionEntry = detail?.versions.find(v => v.version === selectedVersion)
        || detail?.versions[detail.versions.length - 1]
        || null
    const req = versionEntry?.request ?? null

    useEffect(() => {
        if (!req || editing) return
        previewForm.reset(deserializeBanca(req))
    }, [editing, previewForm, req])

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

    const isApproved = detail.status === 'approved'
    const isLatest = selectedVersion === detail.current_version
    const canEdit = isApproved && isLatest
    const editTooltip = !isApproved
        ? 'Edição disponível apenas para bancas aceitas.'
        : !isLatest
            ? 'Edite somente a versão atual; a edição cria uma nova versão.'
            : ''

    function startEdit() {
        editMethods.reset(deserializeBanca(req))
        setEditing(true)
        setSaveStatus(null)
    }

    function cancelEdit() {
        setEditing(false)
        setSaveStatus(null)
    }

    async function saveEdit(e) {
        e.preventDefault()
        setSaving(true)
        setSaveStatus(null)
        try {
            const body = serializeBanca(editMethods.getValues())
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

    async function sendInvites(itemIds, inFlightTag) {
        if (itemIds.length === 0) return
        setSendInFlight(inFlightTag)
        setSendStatus(null)
        try {
            const res = await fetch(`/admin/bancas/${token}/invites/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_ids: itemIds }),
            })
            const data = await res.json()
            if (!res.ok) {
                const msg = typeof data.detail === 'string'
                    ? data.detail
                    : (data.detail?.message || 'Erro ao enviar.')
                setSendStatus({ ok: false, message: msg })
                return
            }
            const okCount = data.results.filter(r => r.ok).length
            const failed = data.results.filter(r => !r.ok)
            setSendStatus({
                ok: failed.length === 0,
                message: failed.length === 0
                    ? `${okCount} envio(s) concluído(s).`
                    : `${okCount} enviado(s), ${failed.length} com falha: ${failed.map(r => `${r.item_id} (${r.error})`).join('; ')}`,
            })
            // Refresh statuses
            const refetch = await fetch(`/admin/bancas/${token}/invites`)
            const refreshed = await refetch.json()
            if (refetch.ok) setInvites(refreshed)
        } catch (err) {
            setSendStatus({ ok: false, message: 'Erro de conexão: ' + err.message })
        } finally {
            setSendInFlight(null)
        }
    }

    const conviteItems = invites.filter(i => i.kind === 'carta_convite')
    const parecerItems = invites.filter(i => i.kind === 'parecer')

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
                <FormProvider {...editMethods}>
                    <form onSubmit={saveEdit}>
                        <BancaGeneralSection />
                        <BancaCompositionSection />
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
                </FormProvider>
            ) : (
                <>
                    <FormProvider {...previewForm}>
                        <BancaGeneralSection disabled />
                        <BancaCompositionSection disabled />
                    </FormProvider>
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

            <section>
                <h2>Envio de Convites e Pareceres</h2>
                {!isApproved && (
                    <p style={{ color: '#6b7280' }}>
                        Disponível apenas após a aprovação da banca.
                    </p>
                )}
                {isApproved && invitesError && <div className="alert alert-err">{invitesError}</div>}
                {isApproved && invitesLoading && <p style={{ color: '#6b7280' }}>Carregando…</p>}

                {isApproved && !invitesLoading && (
                    <>
                        <InviteGroup
                            title="Cartas-convite"
                            items={conviteItems}
                            batchTag="convites"
                            sendInFlight={sendInFlight}
                            onSend={sendInvites}
                        />
                        <InviteGroup
                            title="Pareceres"
                            items={parecerItems}
                            batchTag="pareceres"
                            sendInFlight={sendInFlight}
                            onSend={sendInvites}
                        />
                        {sendStatus && (
                            <div className={sendStatus.ok ? 'alert alert-ok' : 'alert alert-err'}>
                                {sendStatus.message}
                            </div>
                        )}
                    </>
                )}
            </section>
        </div>
    )
}

function InviteGroup({ title, items, batchTag, sendInFlight, onSend }) {
    if (items.length === 0) return null
    const sendableIds = items.filter(i => i.recipient).map(i => i.item_id)
    const busy = !!sendInFlight
    return (
        <div style={{ marginTop: '1rem' }}>
            <h3>{title}</h3>
            <table className="banca-table">
                <thead>
                    <tr>
                        <th>Membro</th>
                        <th>Destinatário</th>
                        <th>Status</th>
                        <th style={{ width: '8rem' }} aria-label="Ações"></th>
                    </tr>
                </thead>
                <tbody>
                    {items.map(item => {
                        const inFlight = sendInFlight === item.item_id
                        return (
                            <tr key={item.item_id}>
                                <td>{item.member_name || '—'}</td>
                                <td>{item.recipient || <span style={{ color: '#b91c1c' }}>sem e-mail</span>}</td>
                                <td>
                                    {item.sent
                                        ? <span style={{ color: '#15803d' }}>Enviado — {formatTimestamp(item.sent_at)}</span>
                                        : <span style={{ color: '#92400e' }}>Não enviado</span>}
                                </td>
                                <td>
                                    <button
                                        type="button"
                                        onClick={() => onSend([item.item_id], item.item_id)}
                                        disabled={busy || !item.recipient}
                                        style={{
                                            padding: '0.35rem 0.75rem',
                                            background: !item.recipient ? '#9ca3af' : '#1f2937',
                                            color: '#fff', border: 'none', borderRadius: 4,
                                            fontSize: '0.85rem',
                                            cursor: (busy || !item.recipient) ? 'not-allowed' : 'pointer',
                                            opacity: busy && !inFlight ? 0.5 : 1,
                                        }}
                                    >
                                        {inFlight ? 'Enviando…' : (item.sent ? 'Reenviar' : 'Enviar')}
                                    </button>
                                </td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>
            <div style={{ marginTop: '0.5rem' }}>
                <button
                    type="button"
                    onClick={() => onSend(sendableIds, batchTag)}
                    disabled={busy || sendableIds.length === 0}
                    style={{
                        padding: '0.6rem 1.5rem',
                        background: sendableIds.length === 0 ? '#9ca3af' : '#3b82f6',
                        color: '#fff', border: 'none', borderRadius: 4, fontSize: '0.95rem',
                        cursor: (busy || sendableIds.length === 0) ? 'not-allowed' : 'pointer',
                    }}
                >
                    {sendInFlight === batchTag ? 'Enviando…' : `Enviar todos (${sendableIds.length})`}
                </button>
            </div>
        </div>
    )
}
