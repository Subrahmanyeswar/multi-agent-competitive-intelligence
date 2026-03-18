import { useEffect, useState } from 'react';
import { getLastReport, getRunHistory, getAnalyses } from '../services/api';
import { FileText, Download, Calendar, Database, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { format, parseISO } from 'date-fns';

const SIG_COLORS = { high: '#dc2626', medium: '#d97706', low: '#16a34a' };

export default function Reports({ refreshKey }) {
  const [latestReport, setLatestReport] = useState(null);
  const [runs, setRuns] = useState([]);
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const [rRes, runsRes, aRes] = await Promise.allSettled([
          getLastReport(), getRunHistory(), getAnalyses()
        ]);
        if (rRes.status === 'fulfilled') setLatestReport(rRes.value.data);
        if (runsRes.status === 'fulfilled') setRuns(runsRes.value.data.runs || []);
        if (aRes.status === 'fulfilled') setAnalyses(aRes.value.data.analyses || []);
      } catch(e) {}
      setLoading(false);
    };
    fetch();
  }, [refreshKey]);

  const successRuns = runs.filter(r => r.status === 'success');
  const lastRun = successRuns[successRuns.length - 1];

  if (loading) return <div style={{ color: 'var(--text-muted)', padding: 20, fontSize: 13 }}>Loading reports...</div>;

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Latest report hero card */}
      {latestReport && !latestReport.error ? (
        <div style={{
          background: 'var(--navy-2)',
          border: '1px solid var(--border)',
          borderRadius: 10,
          padding: '24px 28px',
          marginBottom: 28,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 24,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <div style={{
              width: 56, height: 56, background: 'rgba(37,99,235,0.15)',
              borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center',
              border: '1px solid rgba(59,130,246,0.2)',
            }}>
              <FileText size={24} color="var(--accent-bright)" />
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                Weekly Competitive Intelligence Report
              </div>
              <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Calendar size={11} /> {latestReport.generated_at ? format(parseISO(latestReport.generated_at), 'MMMM d, yyyy HH:mm') : 'Unknown'}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Database size={11} /> {latestReport.size_kb} KB
                </span>
              </div>
              <div style={{ marginTop: 6, fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                {latestReport.filename}
              </div>
            </div>
          </div>
          <a href="/api/report/download" target="_blank" style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '10px 20px', background: 'var(--accent)', borderRadius: 8,
            color: '#fff', fontSize: 13, fontWeight: 500, textDecoration: 'none',
            flexShrink: 0,
          }}>
            <Download size={14} /> Download PDF
          </a>
        </div>
      ) : (
        <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 10, padding: '32px 28px', marginBottom: 28, textAlign: 'center' }}>
          <FileText size={32} color="var(--text-muted)" style={{ margin: '0 auto 12px' }} />
          <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No reports generated yet. Run the pipeline to create your first report.</div>
        </div>
      )}

      {/* Inline report preview */}
      {analyses.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 16 }}>Report Preview — Latest Analysis</div>

          {/* SWOT summary table */}
          <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden', marginBottom: 16 }}>
            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-subtle)', fontSize: 12, color: 'var(--text-secondary)', fontWeight: 500 }}>SWOT Summary</div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  {['Company', 'Top Strength', 'Top Weakness', 'Top Opportunity', 'Top Threat'].map(h => (
                    <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {analyses.map((a, i) => (
                  <tr 
                    key={i} 
                    style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.15s' }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--slate)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{ padding: '10px 12px', fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>{a.company}</td>
                    <td style={{ padding: '10px 12px', fontSize: 12, color: '#4ade80' }}>
                      {a.swot?.strengths?.[0] && !a.swot.strengths[0].includes('pending') ? a.swot.strengths[0] : <span style={{color:'var(--text-muted)',fontStyle:'italic'}}>Run pipeline for data</span>}
                    </td>
                    <td style={{ padding: '10px 12px', fontSize: 12, color: '#f87171' }}>
                      {a.swot?.weaknesses?.[0] && !a.swot.weaknesses[0].includes('pending') ? a.swot.weaknesses[0] : <span style={{color:'var(--text-muted)',fontStyle:'italic'}}>—</span>}
                    </td>
                    <td style={{ padding: '10px 12px', fontSize: 12, color: '#60a5fa' }}>
                      {a.swot?.opportunities?.[0] && !a.swot.opportunities[0].includes('pending') ? a.swot.opportunities[0] : <span style={{color:'var(--text-muted)',fontStyle:'italic'}}>—</span>}
                    </td>
                    <td style={{ padding: '10px 12px', fontSize: 12, color: '#fbbf24' }}>
                      {a.swot?.threats?.[0] && !a.swot.threats[0].includes('pending') ? a.swot.threats[0] : <span style={{color:'var(--text-muted)',fontStyle:'italic'}}>—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Key developments */}
          <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden', marginBottom: 16 }}>
            <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-subtle)', fontSize: 12, color: 'var(--text-secondary)', fontWeight: 500 }}>Key Developments</div>
            {analyses.flatMap(a =>
              (a.key_developments || []).map((dev, i) => (
                <div key={`${a.company}-${i}`} style={{ padding: '12px 14px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', gap: 12 }}>
                  <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 10, fontWeight: 600, color: '#fff', background: SIG_COLORS[dev.significance] || '#475569', alignSelf: 'flex-start', flexShrink: 0 }}>
                    {(dev.significance || 'low').toUpperCase()}
                  </span>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)', marginBottom: 2 }}>{a.company}</div>
                    <div style={{ fontSize: 13, color: 'var(--text-primary)' }}>{dev.title || dev.development}</div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Outlook */}
          {(() => {
            // Find the best available outlook from any analysis
            const outlookText = analyses.find(a => a.outlook && !a.error)?.outlook 
              || analyses.find(a => a.outlook)?.outlook;
            if (!outlookText) return null;
            return (
              <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderLeft: '3px solid var(--accent)', borderRadius: 8, padding: '16px 18px' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>30-Day Outlook</div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7 }}>{outlookText}</div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Run history */}
      <div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 12 }}>All Reports</div>
        <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
          {successRuns.length === 0 ? (
            <div style={{ padding: '20px 14px', fontSize: 13, color: 'var(--text-muted)' }}>No successful runs yet.</div>
          ) : (
            [...successRuns].reverse().map((run, i) => (
              <div 
                key={i} 
                style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', transition: 'background 0.15s' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--slate)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <CheckCircle size={14} color="var(--green)" />
                  <div>
                    <div style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{run.run_id}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {run.started_at ? format(parseISO(run.started_at), 'MMM d, yyyy HH:mm') : ''}
                    </div>
                  </div>
                </div>
                {run.report_path && (
                  <a href="/api/report/download" target="_blank" style={{ fontSize: 12, color: 'var(--accent-bright)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Download size={12} /> PDF
                  </a>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
