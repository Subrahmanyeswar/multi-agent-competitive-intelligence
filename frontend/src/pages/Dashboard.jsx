import { useEffect, useState } from 'react';
import { getCompetitors, getRunHistory, getSignals, getVectorStats } from '../services/api';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { TrendingUp, TrendingDown, Minus, Database, FileText, Activity, Zap } from 'lucide-react';

const Card = ({ children, style }) => (
  <div style={{
    background: 'var(--navy-2)',
    border: '1px solid var(--border-subtle)',
    borderRadius: 8,
    ...style
  }}>{children}</div>
);

const SectionLabel = ({ children }) => (
  <div style={{
    fontSize: 11, fontWeight: 500, letterSpacing: '0.08em',
    textTransform: 'uppercase', color: 'var(--text-muted)',
    marginBottom: 12
  }}>{children}</div>
);

const StatusDot = ({ status }) => {
  const color = status === 'success' ? 'var(--green)' : status === 'failed' ? 'var(--red)' : status === 'running' ? 'var(--amber)' : 'var(--text-muted)';
  return <span style={{ display: 'inline-block', width: 7, height: 7, borderRadius: '50%', background: color, marginRight: 6 }} />;
};

export default function Dashboard({ refreshKey }) {
  const [competitors, setCompetitors] = useState([]);
  const [runs, setRuns] = useState([]);
  const [signals, setSignals] = useState({ topic_signals: [], company_momentum: [] });
  const [vectorStats, setVectorStats] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [compRes, runsRes, sigRes, vecRes] = await Promise.allSettled([
        getCompetitors(), getRunHistory(), getSignals(), getVectorStats()
      ]);
      if (compRes.status === 'fulfilled') setCompetitors(compRes.value.data.competitors || []);
      if (runsRes.status === 'fulfilled') setRuns(runsRes.value.data.runs || []);
      if (sigRes.status === 'fulfilled') setSignals(sigRes.value.data || {});
      if (vecRes.status === 'fulfilled') setVectorStats(vecRes.value.data || {});
    } catch(e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { 
    fetchAll(); 
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, [refreshKey]);

  const lastRun = runs[runs.length - 1];
  const totalArticles = competitors.reduce((s, c) => s + (c.article_count || 0), 0);
  const topSignals = (signals.topic_signals || []).slice(0, 3);

  const metricCards = [
    { label: 'Total Articles', value: totalArticles, icon: FileText, color: 'var(--accent-bright)' },
    { label: 'Companies Tracked', value: competitors.length, icon: Activity, color: 'var(--teal)' },
    { label: 'Signals Detected', value: (signals.topic_signals || []).length, icon: Zap, color: 'var(--amber)' },
    { label: 'Vectors Stored', value: vectorStats.vectors_count || 0, icon: Database, color: 'var(--green)' },
  ];

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200, color: 'var(--text-muted)', fontSize: 13 }}>
      Loading intelligence data...
    </div>
  );

  return (
    <div style={{ maxWidth: 1200 }}>
      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 28 }}>
        {metricCards.map(({ label, value, icon: Icon, color }) => (
          <Card key={label} style={{ padding: '16px 18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>{label}</div>
                <div style={{ fontSize: 28, fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', lineHeight: 1 }}>{value.toLocaleString()}</div>
              </div>
              <div style={{ padding: 8, background: `${color}18`, borderRadius: 6 }}>
                <Icon size={16} color={color} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 28 }}>
        {/* Competitor cards */}
        <div>
          <SectionLabel>Competitors</SectionLabel>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {competitors.map(comp => {
              const momentum = (signals.company_momentum || []).find(m => m.company === comp.name);
              const trend = momentum?.trend;
              const TrendIcon = trend === 'positive' ? TrendingUp : trend === 'negative' ? TrendingDown : Minus;
              const trendColor = trend === 'positive' ? 'var(--green)' : trend === 'negative' ? 'var(--red)' : 'var(--text-muted)';
              return (
                <Card key={comp.name} style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 500, fontSize: 13, color: 'var(--text-primary)', marginBottom: 2 }}>{comp.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{comp.domain}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>{comp.article_count}</div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>articles</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: trendColor, fontSize: 12 }}>
                      <TrendIcon size={14} />
                      {momentum ? `${Math.round((momentum.momentum || 0) * 100)}%` : '—'}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Top signals */}
        <div>
          <SectionLabel>Top Signals This Week</SectionLabel>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {topSignals.length === 0 && (
              <Card style={{ padding: 16 }}>
                <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No signals detected yet. Run the pipeline first.</div>
              </Card>
            )}
            {topSignals.map((sig, i) => {
              const pct = Math.min(Math.round((sig.composite_score || 0) * 100), 100);
              const barColor = pct > 70 ? 'var(--red)' : pct > 40 ? 'var(--amber)' : 'var(--green)';
              return (
                <Card key={i} style={{ padding: '14px 16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <div style={{ fontWeight: 500, fontSize: 13, color: 'var(--text-primary)', textTransform: 'capitalize' }}>
                      {sig.topic?.replace(/_/g, ' ')}
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: barColor }}>
                      {pct}% · {sig.signal_strength || 'weak'}
                    </div>
                  </div>
                  <div style={{ background: 'var(--navy)', borderRadius: 3, height: 4, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${pct}%`, background: barColor, borderRadius: 3, transition: 'width 0.6s ease' }} />
                  </div>
                  <div style={{ marginTop: 6, fontSize: 11, color: 'var(--text-muted)' }}>
                    {sig.companies_involved?.join(', ')} · velocity {(sig.velocity || 0).toFixed(1)}x
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      </div>

      {/* Run history */}
      <div>
        <SectionLabel>Recent Runs</SectionLabel>
        <Card style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                {['Run ID', 'Status', 'Started', 'Duration', 'Articles', 'Report'].map(h => (
                  <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: 11, color: 'var(--text-muted)', fontWeight: 500, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...runs].reverse().slice(0, 8).map((run, i) => {
                let duration = '—';
                if (run.started_at && run.completed_at) {
                  const ms = new Date(run.completed_at) - new Date(run.started_at);
                  duration = `${Math.round(ms / 1000)}s`;
                }
                const articles = Object.values(run.stages || {}).reduce((s, st) => {
                  return s + (st.details?.articles_collected || 0);
                }, 0);
                return (
                  <tr 
                  key={i} 
                  style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.15s', opacity: i > 0 ? 0.7 : 1 }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--slate)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>{run.run_id?.split('_').slice(-2).join('_')}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <StatusDot status={run.status} />
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{run.status}</span>
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: 12, color: 'var(--text-muted)' }}>
                      {run.started_at ? formatDistanceToNow(parseISO(run.started_at), { addSuffix: true }) : '—'}
                    </td>
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>{duration}</td>
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>{articles || '—'}</td>
                    <td style={{ padding: '10px 14px' }}>
                      {run.report_path && (
                        <a href="/api/report/download" target="_blank" style={{ fontSize: 12, color: 'var(--accent-bright)', textDecoration: 'none' }}>Download PDF</a>
                      )}
                    </td>
                  </tr>
                );
              })}
              {runs.length === 0 && (
                <tr><td colSpan={6} style={{ padding: '20px 14px', fontSize: 13, color: 'var(--text-muted)', textAlign: 'center' }}>No runs yet. Press Run Pipeline to start.</td></tr>
              )}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}
