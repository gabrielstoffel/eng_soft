import { useState } from 'react'

import BancaForm, { INITIAL_FORM, serializeBanca } from './BancaForm.jsx'
import { isDevelopment } from '../../env.js'

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
  orientador: {
    gender: 0,
    name: 'Carlos Oliveira',
    institution: 'UFRGS',
    location: 'Porto Alegre, RS',
    lang: 'pt',
    email: 'orientador@ufrgs.br',
  },
  coorientador: {
    gender: 1,
    name: 'Beatriz Lima',
    institution: 'UFRGS',
    location: 'Porto Alegre, RS',
    lang: 'pt',
    email: 'beatriz.lima@ufrgs.br',
  },
  externo1: {
    gender: 1,
    name: 'Ana Costa',
    institution: 'USP',
    location: 'São Paulo, SP',
    lang: 'pt',
    email: 'ana.costa@usp.br',
  },
  externo2: {
    gender: 0,
    name: 'Rafael Mendes',
    institution: 'UNICAMP',
    location: 'Campinas, SP',
    lang: 'pt',
    email: 'rafael.mendes@unicamp.br',
  },
  interno1: {
    gender: 0,
    name: 'Pedro Santos',
    institution: 'UFRGS',
    location: 'Porto Alegre, RS',
    lang: 'pt',
    email: 'pedro.santos@ufrgs.br',
  },
  interno2: {
    gender: 1,
    name: 'Marina Souza',
    institution: 'UFRGS',
    location: 'Porto Alegre, RS',
    lang: 'pt',
    email: 'marina.souza@ufrgs.br',
  },
  supl_int: {
    gender: 0,
    name: 'Lucas Almeida',
    institution: 'UFRGS',
    location: 'Porto Alegre, RS',
    lang: 'pt',
    email: 'lucas.almeida@ufrgs.br',
  },
  supl_ext: {
    gender: 1,
    name: 'Carla Ferreira',
    institution: 'UFSC',
    location: 'Florianópolis, SC',
    lang: 'pt',
    email: 'carla.ferreira@ufsc.br',
  },
}

const FRESH_FORM = isDevelopment ? MOCK : INITIAL_FORM

function formatErrorDetail(detail) {
  if (Array.isArray(detail)) {
    return detail.map((item) => `${item.msg} (${item.loc.join('.')})`).join('; ')
  }
  return detail ?? 'Erro ao enviar pedido.'
}

export default function NewBancaPage() {
  const [form, setForm] = useState(FRESH_FORM)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setStatus(null)

    const body = serializeBanca(form)

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
        setForm(FRESH_FORM)
      } else {
        setStatus({ ok: false, message: formatErrorDetail(data.detail) })
      }
    } catch (err) {
      setStatus({ ok: false, message: `Erro de conexão: ${err.message}` })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>SigBah! — Nova Banca</h1>

      <form onSubmit={handleSubmit}>
        <BancaForm value={form} onChange={setForm} />

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
