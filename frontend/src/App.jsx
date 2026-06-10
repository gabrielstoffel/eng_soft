import { Route, Routes, Navigate } from 'react-router-dom'
import NewBancaPage from './pages/NewBanca/NewBancaPage'
import DecisionPage from './DecisionPage.jsx'
import AdminBancaList from './AdminBancaList.jsx'
import AdminBancaDetail from './AdminBancaDetail.jsx'

function LandingPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100">
      <div className="w-full max-w-md space-y-6 rounded-xl bg-white p-8 shadow-lg">
        <h1 className="text-center text-2xl font-bold text-slate-900">SigBah!</h1>
        <p className="text-center text-sm text-slate-600">Selecione o programa para solicitar uma banca:</p>
        <div className="flex flex-col gap-3">
          <a href="/ppgfis/new" className="block rounded-lg border border-slate-200 px-4 py-4 text-center font-semibold text-slate-800 transition hover:border-sky-300 hover:bg-sky-50">
            PPGFís — Física
          </a>
          <a href="/ppgenfis/new" className="block rounded-lg border border-slate-200 px-4 py-4 text-center font-semibold text-slate-800 transition hover:border-sky-300 hover:bg-sky-50">
            PPGEnFis — Ensino de Física
          </a>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/ppgfis/new" element={<NewBancaPage ppg="ppgfis" />} />
      <Route path="/ppgenfis/new" element={<NewBancaPage ppg="ppgenfis" />} />
      <Route path="/decide/:token" element={<DecisionPage />} />
      <Route path="/admin" element={<AdminBancaList />} />
      <Route path="/admin/banca/:token" element={<AdminBancaDetail />} />
    </Routes>
  )
}
