import { Route, Routes } from 'react-router-dom'
import PetitionForm from './PetitionForm.jsx'
import DecisionPage from './DecisionPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PetitionForm />} />
      <Route path="/decide/:token" element={<DecisionPage />} />
    </Routes>
  )
}
