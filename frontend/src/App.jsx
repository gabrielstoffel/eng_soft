import { Route, Routes } from 'react-router-dom'
import PetitionForm from './PetitionForm.jsx'
import DecisionPage from './DecisionPage.jsx'
import AdminBancaList from './AdminBancaList.jsx'
import AdminBancaDetail from './AdminBancaDetail.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PetitionForm />} />
      <Route path="/decide/:token" element={<DecisionPage />} />
      <Route path="/admin" element={<AdminBancaList />} />
      <Route path="/admin/banca/:token" element={<AdminBancaDetail />} />
    </Routes>
  )
}
