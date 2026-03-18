import { useEffect, useState } from 'react';
import { getAnalyses, getSignals } from '../services/api';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const SIG_COLORS = { high: '#dc2626', medium: '#d97706', low: '#16a34a' };

const SwotQuadrant = ({ label, items, bgColor, borderColor, textColor }) => {
  const hasRealData = items?.length > 0 && !items[0]?.includes('pending') && !items[0]?.includes('Data retrieval');
  return (
    <div style={{
      background: bgColor, border: `1px solid ${borderColor}`,
      borderRadius: 8, padding: '14px 16px', minHeight: 140,
    }}>
      <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', color: textColor, marginBottom: 10 }}>{label}</div>
      {!items?.length && <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', fontStyle: 'italic' }}>Run pipeline to populate</div>}
      {items?.map((item, i) => (
        <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 6, fontSize: 12, color: hasRealData ? 'rgba(255,255,255,0.85)' : 'rgba(255,255,255,0.4)', lineHeight: 1.4, fontStyle: hasRealData ? 'normal' : 'italic' }}>
          <span style={{ color: textColor, marginTop: 2, flexShrink: 0 }}>›</span>
          {item}
        </div>
      ))}
    </div>
  );
};

const MomentumBar = ({ value, label }) => {
  const pct = Math.round((value || 0) * 100);
  const color = pct > 60 ? '#16a34a' : pct < 40 ? '#dc2626' : '#d97706';
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>
        <span>{label}</span>
        <span style={{ fontFamily: 'var(--font-mono)', color }}>{pct}%</span>
      </div>
      <div style={{ height: 6, background: 'var(--navy)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 3, transition: 'width 0.8s ease' }} />
      </div>
    </div>
  );
};

export default function Intelligence({ refreshKey }) {
  const [analyses, setAnalyses] = useState([]);
  const [signals, setSignals] = useState({ topic_signals: [], company_momentum: [] });
  const [selected, setSelected] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const [aRes, sRes] = await Promise.allSettled([getAnalyses(), getSignals()]);
        if (aRes.status === 'fulfilled') setAnalyses(aRes.value.data.analyses || []);
        if (sRes.status === 'fulfilled') setSignals(sRes.value.data || {});
      } catch(e) {}
      setLoading(false);
    };
    fetch();
  }, [refreshKey]);

  const current = analyses[selected];
  const topSignals = (signals.topic_signals || []).slice(0, 8);

  const chartData = {
    labels: topSignals.map(s => s.topic?.replace(/_/g, ' ')),
    datasets: [{
      data: topSignals.map(s => Math.round((s.composite_score || 0) * 100)),
      backgroundColor: topSignals.map(s => {
        const score = (s.composite_score || 0);
        return score > 0.6 ? '#dc262680' : score > 0.3 ? '#d9770680' : '#2563eb80';
      }),
      borderColor: topSignals.map(s => {
        const score = (s.composite_score || 0);
        return score > 0.6 ? '#dc2626' : score > 0.3 ? '#d97706' : '#2563eb';
      }),
      borderWidth: 1, borderRadius: 4,
    }],
  };

  const chartOptions = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: {
      backgroundColor: '#111827',
      titleColor: '#94a3b8',
      bodyColor: '#f1f5f9',
      borderColor: '#1e3a5f',
      borderWidth: 1,
    }},
    scales: {
      x: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { color: '#1e3a5f' } },
      y: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { color: '#1e3a5f' }, max: 100 },
    },
  };

  if (loading) return <div style={{ color: 'var(--text-muted)', padding: 20, fontSize: 13 }}>Loading analyses...</div>;

  if (analyses.length === 0) return (
    <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center', fontSize: 13 }}>
      No analyses available yet. Run the pipeline to generate intelligence data.
    </div>
  );

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Company tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {analyses.map((a, i) => (
          <button key={i} onClick={() => setSelected(i)} style={{
            padding: '7px 16px', borderRadius: 6, fontSize: 13, fontWeight: 500,
            cursor: 'pointer', transition: 'all 0.15s',
            background: selected === i ? 'var(--accent)' : 'var(--navy-2)',
            color: selected === i ? '#fff' : 'var(--text-secondary)',
            border: selected === i ? 'none' : '1px solid var(--border-subtle)',
          }}>
            {a.company}
          </button>
        ))}
      </div>
      {current?.error && (
        <div style={{
          padding: '10px 14px', marginBottom: 16,
          background: 'rgba(217,119,6,0.1)', border: '1px solid rgba(217,119,6,0.3)',
          borderRadius: 6, fontSize: 12, color: '#fbbf24',
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          ⚠ This analysis hit a rate limit during the last run. 
          Run the pipeline again for complete SWOT data.
        </div>
      )}

      {current && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
          {/* SWOT */}
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 12 }}>SWOT Analysis — {current.company}</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <SwotQuadrant label="Strengths" items={current.swot?.strengths} bgColor="#052e16" borderColor="#166534" textColor="#4ade80" />
              <SwotQuadrant label="Weaknesses" items={current.swot?.weaknesses} bgColor="#450a0a" borderColor="#991b1b" textColor="#f87171" />
              <SwotQuadrant label="Opportunities" items={current.swot?.opportunities} bgColor="#0c1a4a" borderColor="#1e40af" textColor="#60a5fa" />
              <SwotQuadrant label="Threats" items={current.swot?.threats} bgColor="#431407" borderColor="#92400e" textColor="#fbbf24" />
            </div>
          </div>

          {/* Right column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Momentum */}
            <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: '16px 18px' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 14 }}>Sentiment Momentum</div>
              {(signals.company_momentum || []).map((m, i) => (
                <MomentumBar key={i} label={m.company} value={m.momentum} />
              ))}
            </div>

            {/* Strategic themes */}
            <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: '16px 18px' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 10 }}>Strategic Themes</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {(current.strategic_themes || []).map((t, i) => (
                  <span key={i} style={{ padding: '4px 10px', background: 'var(--accent-glow)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 20, fontSize: 11, color: 'var(--accent-bright)' }}>{t}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Signal velocity chart */}
      <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: '18px 20px', marginBottom: 24 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 14 }}>Signal Velocity by Topic</div>
        <div style={{ height: 220 }}>
          {topSignals.length > 0
            ? <Bar data={chartData} options={chartOptions} />
            : <div style={{ color: 'var(--text-muted)', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>Run pipeline to populate signal data</div>
          }
        </div>
      </div>

      {/* Key developments */}
      {current && (
        <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-subtle)', fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            Key Developments — {current.company}
          </div>
          {(current.key_developments || []).map((dev, i) => (
            <div key={i} style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 10, fontWeight: 600, color: '#fff', background: SIG_COLORS[dev.significance] || '#475569', flexShrink: 0, marginTop: 1 }}>
                {(dev.significance || 'low').toUpperCase()}
              </span>
              <div>
                <div style={{ fontSize: 13, color: 'var(--text-primary)', marginBottom: 3 }}>{dev.title || dev.development}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{dev.summary || dev.strategic_implication}</div>
              </div>
            </div>
          ))}
          {(!current.key_developments || current.key_developments.length === 0) && (
            <div style={{ padding: 20, fontSize: 13, color: 'var(--text-muted)' }}>No key developments found for this company.</div>
          )}
        </div>
      )}
    </div>
  );
}
