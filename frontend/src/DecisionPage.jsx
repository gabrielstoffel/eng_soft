import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

const TIPO_LABEL = {
  1: 'Dissertação de Mestrado',
  2: 'Exame de Qualificação ao Doutorado',
  3: 'Tese de Doutorado',
}

const STATUS_LABEL = {
  pending: 'Pendente',
  approved: 'Aceita',
  rejected: 'Recusada',
}

const ROLE_LABEL = {
  orientador: 'Orientador(a)',
  coorientador: 'Coorientador(a)',
  externo1: 'Externo 1',
  externo2: 'Externo 2',
  interno1: 'Interno 1',
  interno2: 'Interno 2',
  supl_int: 'Suplente Interno',
  supl_ext: 'Suplente Externo',
}

const ROLES_ORDER = ['orientador', 'coorientador', 'externo1', 'externo2', 'interno1', 'interno2', 'supl_int', 'supl_ext']

const GENDER_LABEL = { 0: 'Masculino', 1: 'Feminino' }

function formatDate(iso) {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}

export default function DecisionPage() {
  const { token } = useParams()
  const [summary, setSummary] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const [loading, setLoading] = useState(true)

  const [showRejectForm, setShowRejectForm] = useState(false)
  const [reason, setReason] = useState('')
  const [observation, setObservation] = useState('')
  const [actionStatus, setActionStatus] = useState(null)
  const [acting, setActing] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const res = await fetch(`/banca/decide/${token}`)
        const data = await res.json()
        if (cancelled) return
        if (res.ok) {
          setSummary(data)
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

  async function postDecision(path, body) {
    setActing(true)
    setActionStatus(null)
    try {
      const res = await fetch(`/banca/decide/${token}/${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
      })
      const data = await res.json()
      if (res.ok) {
        setActionStatus({ ok: true, message: data.message })
        setSummary(s => ({
          ...s,
          status: path === 'approve' ? 'approved' : 'rejected',
          rejection_reason: path === 'reject' ? body.reason : s.rejection_reason,
        }))
        setShowRejectForm(false)
      } else {
        let msg
        if (res.status === 409 && data.detail && typeof data.detail === 'object') {
          msg = data.detail.message || 'Esta banca já foi decidida.'
        } else if (Array.isArray(data.detail)) {
          msg = data.detail.map(d => d.msg + ' (' + d.loc.join('.') + ')').join('; ')
        } else {
          msg = data.detail || 'Erro inesperado.'
        }
        setActionStatus({ ok: false, message: msg })
      }
    } catch (err) {
      setActionStatus({ ok: false, message: 'Erro de conexão: ' + err.message })
    } finally {
      setActing(false)
    }
  }

  if (loading) {
    return <div className="container"><p>Carregando…</p></div>
  }

  if (loadError) {
    return (
      <div className="container">
        <h1>SigBah! — Decisão da Banca</h1>
        <div className="alert alert-err">{loadError}</div>
      </div>
    )
  }

  const { request: req, status, rejection_reason } = summary
  const isPending = status === 'pending'

  return (
    <div className="container">
      <h1>SigBah! — Decisão da Banca</h1>

      <section>
        <h2>Status</h2>
        <div className="row">
          <label>
            Status atual
            <input type="text" value={STATUS_LABEL[status] || status} readOnly />
          </label>
          <label>
            Número da Ata
            <input type="text" value={req.ata} readOnly />
          </label>
        </div>
        {rejection_reason && (
          <label>
            Razão da recusa
            <textarea value={rejection_reason} readOnly rows={3} />
          </label>
        )}
      </section>

      <section>
        <h2>Dados Gerais</h2>

        <div className="row">
          <label>
            Tratamento do(a) aluno(a)
            <input type="text" value={GENDER_LABEL[req.nome.gender]} readOnly />
          </label>
          <label>
            Nome do(a) aluno(a)
            <input type="text" value={req.nome.name} readOnly />
          </label>
        </div>

        <div className="row">
          <label>
            Tipo
            <input type="text" value={TIPO_LABEL[req.tipo] || req.tipo} readOnly />
          </label>
        </div>

        <div className="row">
          <label>
            Data da defesa
            <input type="text" value={formatDate(req.data)} readOnly />
          </label>
          <label>
            Horário
            <input type="text" value={req.horario || '—'} readOnly />
          </label>
          <label>
            Data dos convites
            <input type="text" value={formatDate(req.data_convite)} readOnly />
          </label>
        </div>

        <div className="row">
          <label>
            Local
            <input type="text" value={req.local_banca || '—'} readOnly />
          </label>
          <label>
            Link (videoconferência)
            <input type="text" value={req.link || '—'} readOnly />
          </label>
        </div>

        <label>
          Título (PT)
          <input type="text" value={req.titulo} readOnly />
        </label>
        <label>
          Title (EN)
          <input type="text" value={req.titulo2} readOnly />
        </label>
      </section>

      <section>
        <h2>Membros da Banca</h2>
        {ROLES_ORDER.map(role => {
          const m = req[role]
          if (!m) return null
          return (
            <fieldset key={role}>
              <legend>{ROLE_LABEL[role]}</legend>
              <div className="member-grid">
                <label>
                  Tratamento
                  <input
                    type="text"
                    value={m.gender === 1 ? 'Profª. Drª.' : 'Prof. Dr.'}
                    readOnly
                  />
                </label>
                <label>
                  Nome
                  <input type="text" value={m.name} readOnly />
                </label>
                <label>
                  Instituição
                  <input type="text" value={m.institution} readOnly />
                </label>
                <label>
                  Localidade
                  <input type="text" value={m.location} readOnly />
                </label>
                <label>
                  Idioma da carta
                  <input type="text" value={m.lang === 'en' ? 'English' : 'Português'} readOnly />
                </label>
                <label>
                  E-mail
                  <input type="text" value={m.email || '—'} readOnly />
                </label>
              </div>
            </fieldset>
          )
        })}
      </section>

      {actionStatus && (
        <div className={actionStatus.ok ? 'alert alert-ok' : 'alert alert-err'}>
          {actionStatus.message}
        </div>
      )}

      {isPending && !showRejectForm && (
        <section>
          <label>
            Observação (opcional)
            <textarea
              rows={2}
              value={observation}
              onChange={e => setObservation(e.target.value)}
              placeholder="Ex: aguardando texto do aluno, aguardando press release..."
            />
          </label>
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button
              type="button"
              onClick={() => postDecision('approve', observation ? { observation } : undefined)}
              disabled={acting}
              style={{
                flex: 1, padding: '0.7rem 2rem', background: '#16a34a', color: '#fff',
                border: 'none', borderRadius: 4, fontSize: '1rem', cursor: 'pointer',
                opacity: acting ? 0.6 : 1,
              }}
            >
              {acting ? 'Processando…' : 'Aceitar'}
            </button>
            <button
              type="button"
              onClick={() => setShowRejectForm(true)}
              disabled={acting}
              style={{
                flex: 1, padding: '0.7rem 2rem', background: '#dc2626', color: '#fff',
                border: 'none', borderRadius: 4, fontSize: '1rem', cursor: 'pointer',
              }}
            >
              Recusar
            </button>
          </div>
        </section>
      )}

      {isPending && showRejectForm && (
        <section>
          <h2>Razão da recusa</h2>
          <label>
            Descreva a razão *
            <textarea
              required
              rows={4}
              value={reason}
              onChange={e => setReason(e.target.value)}
              placeholder="Por que esta banca está sendo recusada?"
            />
          </label>
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button
              type="button"
              onClick={() => { setShowRejectForm(false); setReason('') }}
              disabled={acting}
              style={{
                flex: 1, padding: '0.7rem 2rem', background: '#6b7280', color: '#fff',
                border: 'none', borderRadius: 4, fontSize: '1rem', cursor: 'pointer',
              }}
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => postDecision('reject', { reason: reason.trim() })}
              disabled={acting || reason.trim().length === 0}
              style={{
                flex: 1, padding: '0.7rem 2rem', background: '#dc2626', color: '#fff',
                border: 'none', borderRadius: 4, fontSize: '1rem', cursor: 'pointer',
                opacity: (acting || reason.trim().length === 0) ? 0.6 : 1,
              }}
            >
              {acting ? 'Processando…' : 'Confirmar Recusa'}
            </button>
          </div>
        </section>
      )}
    </div>
  )
}
