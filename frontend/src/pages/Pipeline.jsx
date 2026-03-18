import { useEffect, useState, useRef } from 'react';
import { getPipelineStatus, getRunHistory } from '../services/api';
import { Search, Cpu, Database, Brain, FileText, CheckCircle, Clock, AlertCircle, Loader, Settings } from 'lucide-react';

const STAGES = [
  {
    id: 'config_validation', label: 'Manager Agent', icon: Settings,
    description: 'The Chief Intelligence Officer validates configuration, loads competitor list, assigns tasks to specialist agents, and coordinates the full workflow.',
    color: '#7c3aed',
  },
  {
    id: 'scraping', label: 'Research Agents', icon: Search,
    description: 'Three parallel Research Agents scrape Google News, TechCrunch, Reuters, and Bloomberg for each competitor using Serper API and Firecrawl.',
    color: '#0d9488',
  },
  {
    id: 'ingestion', label: 'Ingestion Pipeline', icon: Database,
    description: 'Raw articles are cleaned, chunked into 500-token segments, embedded using all-MiniLM-L6-v2, and upserted to Qdrant vector DB with metadata.',
    color: '#2563eb',
  },
  {
    id: 'analysis', label: 'Analysis Agent', icon: Brain,
    description: 'Mistral AI retrieves context via RAG from Qdrant, applies SWOT framework, Porter\'s Five Forces, and weak signal scoring to each competitor.',
    color: '#7c3aed',
  },
  {
    id: 'synthesis', label: 'Synthesizer Agent', icon: Cpu,
    description: 'The Synthesizer takes all company analyses and generates a unified executive report with strategic recommendations and 30-day outlook.',
    color: '#d97706',
  },
  {
    id: 'rendering', label: 'Report Generator', icon: FileText,
    description: 'ReportLab renders the final PDF with executive summary, SWOT tables, weak signals, and actionable competitive recommendations.',
    color: '#16a34a',
  },
];

const STATUS_ICON = {
  idle: Clock,
  active: Loader,
  complete: CheckCircle,
  error: AlertCircle,
};

const STATUS_COLOR = {
  idle: 'var(--text-muted)',
  active: 'var(--accent-bright)',
  complete: 'var(--green)',
  error: 'var(--red)',
};

export default function Pipeline({ refreshKey }) {
  const [status, setStatus] = useState({ running: false, stage: '', message: '' });
  const [runs, setRuns] = useState([]);
  const [selectedStage, setSelectedStage] = useState(null);
  const logRef = useRef(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [statusRes, runsRes] = await Promise.all([getPipelineStatus(), getRunHistory()]);
        setStatus(statusRes.data);
        setRuns(runsRes.data.runs || []);
      } catch(e) {}
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [refreshKey]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [runs]);

  const getStageStatus = (stageId) => {
    if (status.stage === 'complete' && !status.running) return 'complete';
    if (status.stage === stageId) return 'active';
    const stageOrder = ['config_validation', 'scraping', 'ingestion', 'analysis', 'synthesis', 'rendering'];
    const currentIdx = stageOrder.indexOf(status.stage);
    const thisIdx = stageOrder.indexOf(stageId);
    if (status.running && thisIdx < currentIdx) return 'complete';
    if (!status.running && status.stage === 'complete') return 'complete';
    return 'idle';
  };

  const lastRun = runs[runs.length - 1];
  const logLines = [];
  if (lastRun?.stages) {
    Object.entries(lastRun.stages).forEach(([stage, data]) => {
      logLines.push({ time: data.timestamp?.slice(11, 19) || '', level: data.status === 'success' ? 'OK' : 'INFO', msg: `[${stage}] ${data.status}` });
    });
  }
  if (status.message) {
    logLines.push({ time: new Date().toISOString().slice(11, 19), level: 'LIVE', msg: status.message });
  }

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Pipeline flow diagram */}
      <div style={{
        background: 'var(--navy-2)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 10,
        padding: '28px 24px',
        marginBottom: 24,
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 24 }}>
          Pipeline Flow
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 0, overflowX: 'auto', paddingBottom: 8 }}>
          {STAGES.map((stage, i) => {
            const stageStatus = getStageStatus(stage.id);
            const Icon = stage.icon;
            const isActive = stageStatus === 'active';
            const isComplete = stageStatus === 'complete';
            return (
              <div key={stage.id} style={{ display: 'flex', alignItems: 'center', flex: i < STAGES.length - 1 ? 'none' : 1 }}>
                <div
                  onClick={() => setSelectedStage(selectedStage?.id === stage.id ? null : stage)}
                  style={{
                    display: 'flex', flexDirection: 'column', alignItems: 'center',
                    width: 140, cursor: 'pointer',
                    padding: '16px 8px',
                    borderRadius: 8,
                    border: `1px solid ${isActive ? stage.color : isComplete ? `${stage.color}40` : 'var(--border-subtle)'}`,
                    background: isActive ? `${stage.color}12` : isComplete ? `${stage.color}08` : 'transparent',
                    transition: 'all 0.3s ease',
                    boxShadow: isActive ? `0 0 16px ${stage.color}30` : 'none',
                    animation: isActive ? 'pulse 2s ease-in-out infinite' : 'none',
                  }}
                >
                  <div style={{
                    width: 36, height: 36, borderRadius: 8,
                    background: isActive ? stage.color : isComplete ? `${stage.color}30` : 'var(--slate)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: 8, transition: 'all 0.3s',
                  }}>
                    <Icon size={16} color={isActive ? '#fff' : isComplete ? stage.color : 'var(--text-muted)'} />
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 500, color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)', textAlign: 'center', lineHeight: 1.3 }}>
                    {stage.label}
                  </div>
                  <div style={{ marginTop: 6, fontSize: 10, color: STATUS_COLOR[stageStatus], display: 'flex', alignItems: 'center', gap: 3 }}>
                    {isActive && <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-bright)', display: 'inline-block', animation: 'blink 1s ease-in-out infinite' }} />}
                    {stageStatus}
                  </div>
                </div>

                {i < STAGES.length - 1 && (
                  <div style={{ width: 40, height: 2, position: 'relative', flexShrink: 0 }}>
                    <div style={{ width: '100%', height: '100%', background: 'var(--border-subtle)', borderRadius: 1 }} />
                    {(isActive || isComplete) && (
                      <div style={{
                        position: 'absolute', top: 0, left: 0,
                        width: isComplete ? '100%' : '60%',
                        height: '100%',
                        background: stage.color,
                        borderRadius: 1,
                        transition: 'width 0.5s ease',
                      }} />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {status.running && (
          <div style={{ marginTop: 16, padding: '8px 12px', background: 'var(--accent-glow)', borderRadius: 6, border: '1px solid rgba(59,130,246,0.2)', fontSize: 12, color: 'var(--accent-bright)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-bright)', display: 'inline-block', animation: 'blink 1s ease-in-out infinite' }} />
            {status.message || 'Pipeline running...'}
          </div>
        )}
      </div>

      {/* Stage detail */}
      {selectedStage && (
        <div style={{
          background: 'var(--navy-2)',
          border: `1px solid ${selectedStage.color}40`,
          borderLeft: `3px solid ${selectedStage.color}`,
          borderRadius: 8, padding: '16px 20px', marginBottom: 24,
          fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7,
        }}>
          <div style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>{selectedStage.label}</div>
          {selectedStage.description}
        </div>
      )}

      {/* Log terminal */}
      <div style={{
        background: '#0a0a0a',
        border: '1px solid var(--border-subtle)',
        borderRadius: 8, overflow: 'hidden',
      }}>
        <div style={{ padding: '8px 14px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }} />
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b' }} />
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#22c55e' }} />
          <span style={{ marginLeft: 8, fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>pipeline.log</span>
        </div>
        <div ref={logRef} style={{ padding: '12px 16px', height: 240, overflowY: 'auto', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
          {logLines.length === 0 && (
            <div style={{ color: 'var(--text-muted)' }}>$ Waiting for pipeline run...</div>
          )}
          {logLines.map((line, i) => (
            <div key={i} style={{ marginBottom: 2, display: 'flex', gap: 12 }}>
              <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>{line.time}</span>
              <span style={{ color: line.level === 'OK' ? '#22c55e' : line.level === 'LIVE' ? 'var(--accent-bright)' : '#f59e0b', flexShrink: 0 }}>[{line.level}]</span>
              <span style={{ color: '#cbd5e1' }}>{line.msg}</span>
            </div>
          ))}
          {status.running && (
            <div style={{ color: 'var(--accent-bright)', animation: 'blink 1s ease-in-out infinite' }}>▊</div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.85} }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
      `}</style>
    </div>
  );
}
