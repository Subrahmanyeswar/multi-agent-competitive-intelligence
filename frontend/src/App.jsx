import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import ConnectionStatus from './components/layout/ConnectionStatus';
import Dashboard from './pages/Dashboard';
import Pipeline from './pages/Pipeline';
import Agents from './pages/Agents';
import Intelligence from './pages/Intelligence';
import SignalGraph from './pages/SignalGraph';
import Reports from './pages/Reports';
import DataStore from './pages/DataStore';

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/pipeline': 'Live Pipeline',
  '/agents': 'Agent Activity',
  '/intelligence': 'Intelligence Analysis',
  '/graph': 'Signal Graph',
  '/reports': 'Reports',
  '/data': 'Data Store',
};

function AppContent({ refreshKey, setRefreshKey }) {
  const location = useLocation();
  const currentTitle = PAGE_TITLES[location.pathname] || 'Intelligence';

  useEffect(() => {
    document.title = `${currentTitle} — Competitive Intelligence`;
  }, [currentTitle]);

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopBar title={currentTitle} onRunComplete={() => setRefreshKey(k => k + 1)} />
        <ConnectionStatus />
        <main style={{ flex: 1, overflow: 'auto', padding: 24, background: 'var(--navy)' }}>
          <Routes>
            <Route path="/" element={<Dashboard refreshKey={refreshKey} />} />
            <Route path="/pipeline" element={<Pipeline refreshKey={refreshKey} />} />
            <Route path="/agents" element={<Agents refreshKey={refreshKey} />} />
            <Route path="/intelligence" element={<Intelligence refreshKey={refreshKey} />} />
            <Route path="/graph" element={<SignalGraph refreshKey={refreshKey} />} />
            <Route path="/reports" element={<Reports refreshKey={refreshKey} />} />
            <Route path="/data" element={<DataStore refreshKey={refreshKey} />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let wasRunning = false;
    const poll = setInterval(async () => {
      try {
        const res = await import('./services/api').then(m => m.getPipelineStatus());
        const isRunning = res.data.running;
        if (wasRunning && !isRunning && res.data.stage === 'complete') {
          // Pipeline just finished — refresh all data
          setRefreshKey(k => k + 1);
        }
        wasRunning = isRunning;
      } catch(e) {}
    }, 5000);
    return () => clearInterval(poll);
  }, []);

  return (
    <BrowserRouter>
      <AppContent refreshKey={refreshKey} setRefreshKey={setRefreshKey} />
    </BrowserRouter>
  );
}
