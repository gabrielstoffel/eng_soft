import {
  IconAdjustmentsHorizontal,
  IconFileSearch,
  IconEye,
  IconSearch,
} from '@tabler/icons-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import SelectInput from './components/SelectInput'
import TextInput from './components/TextInput'

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

const STATUS_TONE = {
  pending: 'bg-amber-50 text-amber-800 ring-1 ring-amber-200',
  approved: 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200',
  rejected: 'bg-rose-50 text-rose-800 ring-1 ring-rose-200',
}

function formatDate(iso) {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}

function ResultMeta({ label, value }) {
  return (
    <div className="space-y-1">
      <div className="text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
        {label}
      </div>
      <div className="text-sm font-medium text-slate-800">{value || '—'}</div>
    </div>
  )
}

export default function AdminBancaList() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState({
    status: '',
    ata: '',
    ppg: '',
    q: '',
  })
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    const handle = setTimeout(() => {
      const params = new URLSearchParams()
      if (filters.status) params.set('status', filters.status)
      if (filters.ata) params.set('ata', filters.ata)
      if (filters.ppg) params.set('ppg', filters.ppg)
      if (filters.q) params.set('q', filters.q)
      const qs = params.toString()
      const url = qs ? `/admin/bancas?${qs}` : '/admin/bancas'

      setLoading(true)
      setError(null)
      fetch(url)
        .then(async (res) => {
          const data = await res.json()
          if (cancelled) return
          if (res.ok) {
            setItems(data)
          } else {
            setError(
              typeof data.detail === 'string'
                ? data.detail
                : 'Erro ao listar bancas.',
            )
          }
        })
        .catch((err) => {
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
  }, [
    filters.status,
    filters.ata,
    filters.ppg,
    filters.q,
  ])

  function setF(field, value) {
    setFilters((f) => ({ ...f, [field]: value }))
  }

  return (
    <div className="min-h-screen bg-stone-100 text-slate-900">
      <div className="mx-auto w-full max-w-6xl px-3 py-8 sm:px-6 lg:px-8 lg:py-10">
        <header className="mb-6 space-y-2">
          <div className="text-xs font-semibold tracking-[0.18em] text-sky-700 uppercase">
            Administração
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
            Bancas cadastradas
          </h1>
        </header>

        <section className="overflow-hidden rounded-xl bg-white shadow-[0_20px_50px_-40px_rgba(15,23,42,0.35)]">
          <div className="space-y-8 px-4 py-6 sm:px-8 sm:py-8">
            <div className="space-y-6 border-b border-slate-200 pb-8">
              <div className="flex items-center gap-1">
                <IconAdjustmentsHorizontal
                  aria-hidden="true"
                  size={18}
                  stroke={1.9}
                  className="shrink-0 self-center text-sky-700"
                />
                <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">
                  Filtros
                </h3>
              </div>

              <label className="flex min-w-0 flex-1 flex-col gap-1.5">
                <span className="text-sm font-semibold leading-5 text-slate-800">
                  Busca livre
                </span>
                <div className="relative">
                  <IconSearch
                    aria-hidden="true"
                    size={17}
                    stroke={1.9}
                    className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
                  />
                  <TextInput
                    type="text"
                    value={filters.q}
                    onChange={(e) => setF('q', e.target.value)}
                    placeholder="Nome, orientador, título…"
                    className="pl-11"
                  />
                </div>
              </label>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-2">
                <label className="flex min-w-0 flex-1 flex-col gap-1.5">
                  <span className="text-sm font-semibold leading-5 text-slate-800">
                    Status
                  </span>
                  <SelectInput
                    value={filters.status}
                    onChange={(e) => setF('status', e.target.value)}
                  >
                    <option value="">Todos</option>
                    <option value="pending">Pendente</option>
                    <option value="approved">Aceita</option>
                    <option value="rejected">Recusada</option>
                  </SelectInput>
                </label>

                <label className="flex min-w-0 flex-1 flex-col gap-1.5">
                  <span className="text-sm font-semibold leading-5 text-slate-800">
                    Programa (PPG)
                  </span>
                  <SelectInput
                    value={filters.ppg}
                    onChange={(e) => setF('ppg', e.target.value)}
                  >
                    <option value="">Todos</option>
                    <option value="ppgfis">PPGFís</option>
                    <option value="ppgenfis">PPGEnFis</option>
                  </SelectInput>
                </label>

                <label className="flex min-w-0 flex-1 flex-col gap-1.5">
                  <span className="text-sm font-semibold leading-5 text-slate-800">
                    Ata
                  </span>
                  <TextInput
                    type="number"
                    min={1}
                    value={filters.ata}
                    onChange={(e) => setF('ata', e.target.value)}
                  />
                </label>
              </div>
            </div>

            {error ? (
              <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
                {error}
              </div>
            ) : null}

            <div className="space-y-6">
              <div className="flex items-center gap-1">
                <IconFileSearch
                  aria-hidden="true"
                  size={18}
                  stroke={1.9}
                  className="shrink-0 self-center text-sky-700"
                />
                <h3 className="text-sm font-semibold tracking-[0.12em] text-slate-900 uppercase">
                  Resultados
                </h3>
              </div>

              {!loading && items.length === 0 && !error ? (
                <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
                  Nenhuma banca encontrada para os filtros atuais.
                </div>
              ) : null}

              {items.length > 0 ? (
                <>
                  <div className="hidden overflow-hidden rounded-xl border border-slate-200 lg:block">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className="bg-slate-50">
                          <th className="px-4 py-3 text-left text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                            Ata
                          </th>
                          <th className="px-4 py-3 text-left text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                            Aluno(a)
                          </th>
                          <th className="px-4 py-3 text-left text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                            Tipo
                          </th>
                          <th className="px-4 py-3 text-left text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                            Data
                          </th>
                          <th className="px-4 py-3 text-left text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                            Orientador(a)
                          </th>
                          <th className="px-4 py-3 text-left text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                            Status
                          </th>
                          <th className="px-4 py-3 text-left text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                            Versão
                          </th>
                          <th className="px-4 py-3" />
                        </tr>
                      </thead>
                      <tbody>
                        {items.map((it) => (
                          <tr
                            key={it.decision_token}
                            className="border-t border-slate-200 transition hover:bg-slate-50"
                          >
                            <td className="px-4 py-4 text-sm font-semibold text-slate-900">
                              {it.ata}
                            </td>
                            <td className="px-4 py-4 text-sm text-slate-800">
                              {it.student_name}
                            </td>
                            <td className="px-4 py-4 text-sm text-slate-700">
                              {TIPO_LABEL[it.tipo] || it.tipo}
                            </td>
                            <td className="px-4 py-4 text-sm text-slate-700">
                              {formatDate(it.data)}
                            </td>
                            <td className="px-4 py-4 text-sm text-slate-700">
                              {it.orientador_name}
                            </td>
                            <td className="px-4 py-4">
                              <span
                                className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${STATUS_TONE[it.status] || 'bg-slate-100 text-slate-700 ring-1 ring-slate-200'}`}
                              >
                                {STATUS_LABEL[it.status] || it.status}
                              </span>
                            </td>
                            <td className="px-4 py-4 text-sm text-slate-700">
                              v{it.current_version}
                            </td>
                            <td className="px-4 py-4 text-right">
                              <button
                                type="button"
                                onClick={() =>
                                  navigate(`/admin/banca/${it.decision_token}`)
                                }
                                className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium leading-none text-slate-700 transition hover:border-slate-400 hover:bg-slate-100"
                              >
                                Ver
                                <IconEye
                                  aria-hidden="true"
                                  size={15}
                                  stroke={2}
                                  className="shrink-0"
                                />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="space-y-3 lg:hidden">
                    {items.map((it) => (
                      <article
                        key={it.decision_token}
                        className="rounded-xl border border-slate-200 bg-slate-50/60 p-4"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="space-y-1">
                            <div className="text-[0.72rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                              Ata {it.ata}
                            </div>
                            <h3 className="text-lg font-semibold text-slate-950">
                              {it.student_name}
                            </h3>
                          </div>
                          <span
                            className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${STATUS_TONE[it.status] || 'bg-slate-100 text-slate-700 ring-1 ring-slate-200'}`}
                          >
                            {STATUS_LABEL[it.status] || it.status}
                          </span>
                        </div>

                        <div className="mt-4 grid gap-4 sm:grid-cols-2">
                          <ResultMeta
                            label="Tipo"
                            value={TIPO_LABEL[it.tipo] || it.tipo}
                          />
                          <ResultMeta label="Data" value={formatDate(it.data)} />
                          <ResultMeta
                            label="Orientador(a)"
                            value={it.orientador_name}
                          />
                          <ResultMeta
                            label="Versão"
                            value={`v${it.current_version}`}
                          />
                        </div>

                        <div className="mt-4">
                          <button
                            type="button"
                            onClick={() =>
                              navigate(`/admin/banca/${it.decision_token}`)
                            }
                            className="inline-flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium leading-none text-slate-700 transition hover:border-slate-400 hover:bg-slate-100"
                          >
                            Ver
                            <IconEye
                              aria-hidden="true"
                              size={15}
                              stroke={2}
                              className="shrink-0"
                            />
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                </>
              ) : null}
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
