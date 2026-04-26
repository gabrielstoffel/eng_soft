import { useState } from 'react'
import MemberField from './MemberField.jsx'

const EMPTY_MEMBER = { gender: 0, name: '', institution: '', location: '', lang: 'pt' }

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

function coerceMember(m) {
  if (!m) return null
  return { ...m, gender: Number(m.gender) }
}

export default function App() {
  const [form, setForm] = useState(INITIAL)
  const [status, setStatus] = useState(null) // { ok: bool, message: string }
  const [loading, setLoading] = useState(false)

  function set(field, value) {
    setForm(f => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setStatus(null)

    const body = {
      ...form,
      tipo: Number(form.tipo),
      ata: Number(form.ata),
      nome: { ...form.nome, gender: Number(form.nome.gender) },
      data_convite: form.data_convite || null,
      local_banca: form.local_banca || null,
      link: form.link || null,
      orientador: coerceMember(form.orientador),
      coorientador: coerceMember(form.coorientador),
      externo1: coerceMember(form.externo1),
      externo2: coerceMember(form.externo2),
      interno1: coerceMember(form.interno1),
      interno2: coerceMember(form.interno2),
      supl_int: coerceMember(form.supl_int),
      supl_ext: coerceMember(form.supl_ext),
    }

    try {
      const res = await fetch('/banca', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (res.ok) {
        setStatus({ ok: true, message: `E-mails enviados! Banca #${data.ata} — ${data.student_name}` })
        setForm(INITIAL)
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
              <select value={form.tipo} onChange={e => set('tipo', e.target.value)}>
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

          <MemberField label="Orientador(a) *" value={form.orientador} onChange={v => set('orientador', v)} required />
          <MemberField label="Coorientador(a)" value={form.coorientador} onChange={v => set('coorientador', v)} />
          <MemberField label="Externo 1 *" value={form.externo1} onChange={v => set('externo1', v)} required />
          <MemberField label="Externo 2" value={form.externo2} onChange={v => set('externo2', v)} />
          <MemberField label="Interno 1 *" value={form.interno1} onChange={v => set('interno1', v)} required />
          <MemberField label="Interno 2 *" value={form.interno2} onChange={v => set('interno2', v)} required />
          <MemberField label="Suplente Interno" value={form.supl_int} onChange={v => set('supl_int', v)} />
          <MemberField label="Suplente Externo" value={form.supl_ext} onChange={v => set('supl_ext', v)} />
        </section>

        {status && (
          <div className={status.ok ? 'alert alert-ok' : 'alert alert-err'}>
            {status.message}
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Enviando...' : 'Criar Banca e Enviar E-mails'}
        </button>
      </form>
    </div>
  )
}
