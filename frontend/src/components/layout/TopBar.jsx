import { useState } from 'react';
import { Play, RefreshCw, Clock } from 'lucide-react';
import { runPipeline } from '../../services/api';
import { format } from 'date-fns';

export default function TopBar({ title, onRunComplete }) {
  const [running, setRunning] = useState(false);
  const [lastRun, setLastRun] = useState(null);
  const [statusMsg, setStatusMsg] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);

  const handleRun = async () => {
    setRunning(true);
    setStatusMsg('Starting pipeline...');
    try {
      await runPipeline();
      setLastRun(new Date());
      setStatusMsg('Pipeline started — check Live Pipeline page for progress');
    } catch (e) {
      setStatusMsg('Failed to start — is the backend running?');
      setTimeout(() => { setRunning(false); setStatusMsg(''); }, 4000);
      return;
    }
    
    // Poll for completion
    const poll = setInterval(async () => {
      try {
        const { getPipelineStatus } = await import('../../services/api');
        const res = await getPipelineStatus();
        if (!res.data.running && res.data.stage === 'complete') {
          clearInterval(poll);
          setRunning(false);
          setStatusMsg('Run complete — report ready');
          setShowSuccess(true);
          onRunComplete?.();
          setTimeout(() => { setStatusMsg(''); setShowSuccess(false); }, 5000);
        } else if (!res.data.running && res.data.stage === 'error') {
          clearInterval(poll);
          setRunning(false);
          setStatusMsg(`Error: ${res.data.message}`);
          setTimeout(() => setStatusMsg(''), 6000);
        } else {
          setStatusMsg(res.data.message || 'Pipeline running...');
        }
      } catch(e) {}
    }, 4000);
  };

  return (
    <header style={{
      height: 56,
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      background: 'var(--navy-2)',
      flexShrink: 0,
    }}>
      <h1 style={{ fontSize: 15, fontWeight: 500, color: 'var(--text-primary)' }}>{title}</h1>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {lastRun && (
          <span style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <Clock size={12} />
            Last run: {format(lastRun, 'HH:mm')}
          </span>
        )}
        {statusMsg && (
          <span style={{ fontSize: 12, color: 'var(--accent-bright)' }}>{statusMsg}</span>
        )}
        <button onClick={handleRun} disabled={running} style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: '7px 14px',
          background: running ? 'var(--slate)' : 'var(--accent)',
          border: 'none', borderRadius: 6,
          color: '#fff', fontSize: 13, fontWeight: 500,
          cursor: running ? 'not-allowed' : 'pointer',
          transition: 'all 0.15s',
        }}>
          {running
            ? <><RefreshCw size={13} style={{ animation: 'spin 1s linear infinite' }} /> Running...</>
            : <><Play size={13} /> Run Pipeline</>
          }
        </button>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </header>
  );
}
