import { Routes, Route } from 'react-router-dom';
import { HomePage } from '@/pages/HomePage';
import { ArenaPage } from '@/pages/ArenaPage';
import { ContractPage } from '@/pages/ContractPage';
import { HistoryPage } from '@/pages/HistoryPage';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="/arena/:id" element={<ArenaPage />} />
      <Route path="/contract/:id" element={<ContractPage />} />
    </Routes>
  );
}
