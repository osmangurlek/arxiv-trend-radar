import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'
import Ingest from './pages/Ingest.jsx'
import Trends from './pages/Trends.jsx'
import EntityExplorer from './pages/EntityExplorer.jsx'
import Digest from './pages/Digest.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="ingest" element={<Ingest />} />
          <Route path="trends" element={<Trends />} />
          <Route path="entities" element={<EntityExplorer />} />
          <Route path="digest" element={<Digest />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
