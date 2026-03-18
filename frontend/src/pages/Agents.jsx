import { useEffect, useState } from 'react';
import { getRunHistory, getCompetitors } from '../services/api';
import { Search, Brain, Cpu, Shield, Settings } from 'lucide-react';

const AGENTS = [
  {
    id: 'manager', name: 'Manager Agent', role: 'Orchestrator',
    icon: Settings, color: '#7c3aed',
    description: 'The Chief Intelligence Officer. Plans the workflow, delegates tasks to specialist agents, and validates outputs before finalizing.',
    tools: ['CrewAI hierarchical process', 'Task delegation', 'Output validation'],
    model: 'Mistral Large',
  },
  {
    id: 'research', name: 'Research Agent', role: 'Data Collector',
    icon: Search, color: '#0d9488',
    description: 'Market Intelligence Data Collector. Scrapes news from Google News, TechCrunch, Reuters, and Bloomberg for each competitor.',
    tools: ['Serper API (Google News)', 'Firecrawl (web scraper)', 'Rate-limited retries'],
    model: 'Mistral Large',
  },
  {
    id: 'analysis', name: 'Analysis Agent', role: 'Strategy Analyst',
    icon: Brain, color: '#2563eb',
    description: 'Strategy Consultant. Retrieves context via RAG from Qdrant, applies SWOT, Porter\'s Five Forces, and weak signal scoring.',
    tools: ['RAG (Qdrant vector search)', 'SWOT framework', 'Signal velocity scoring', 'Sentiment momentum'],
    model: 'Mistral Large',
  },
  {
    id: 'synthesizer', name: 'Synthesizer Agent', role: 'Report Writer',
    icon: Cpu, color: '#d97706',
    description: 'Executive Report Writer. Takes all company analyses and synthesizes a unified competitive landscape report with strategic recommendations.',
    tools: ['Multi-company synthesis', 'Recommendation engine', 'Citation tracking'],
    model: 'Mistral Large',
  },
  {
    id: 'qc', name: 'Quality Guard', role: 'Validation',
    icon: Shield, color: '#16a34a',
    description: 'JSON schema validation, error recovery, and fallback analysis generation when LLM calls fail or return malformed data.',
    tools: ['Pydantic validation', 'Fallback analysis', 'Retry logic (3 attempts)'],
    model: 'Rule-based',
  },
];

export default function Agents({ refreshKey }) {
  const [runs, setRuns] = useState([]);
  const [competitors, setCompetitors] = useState([]);

  useEffect(() => {
    const fetch = async () => {
      try {
        const [rRes, cRes] = await Promise.all([getRunHistory(), getCompetitors()]);
        setRuns(rRes.data.runs || []);
        setCompetitors(cRes.data.competitors || []);
      } catch(e) {}
    };
    fetch();
  }, [refreshKey]);

  const lastRun = runs[runs.length - 1];
  const getAgentActivity = (agentId) => {
    if (!lastRun?.stages) return null;
    const stageMap = { manager: 'config_validation', research: 'ingestion', analysis: 'analysis', synthesizer: 'synthesis', qc: 'pdf_render' };
    return lastRun.stages[stageMap[agentId]];
  };

  return (
    <div style={{ maxWidth: 1100 }}>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 16 }}>
        Agent Roster — {AGENTS.length} Specialized Agents
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16, marginBottom: 28 }}>
        {AGENTS.map(agent => {
          const Icon = agent.icon;
          const activity = getAgentActivity(agent.id);
          const isActive = activity?.status === 'running';
          const isDone = activity?.status === 'success';
          return (
            <div key={agent.id} style={{
              background: 'var(--navy-2)',
              border: `1px solid ${isActive ? agent.color + '60' : 'var(--border-subtle)'}`,
              borderRadius: 10, padding: '20px',
              boxShadow: isActive ? `0 0 20px ${agent.color}20` : 'none',
              transition: 'all 0.3s',
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 8, background: agent.color + '20', border: `1px solid ${agent.color}40`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={18} color={agent.color} />
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>{agent.name}</div>
                    <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 20, background: agent.color + '20', color: agent.color, fontWeight: 500 }}>{agent.role}</span>
                  </div>
                </div>
                <div style={{ fontSize: 10, color: isDone ? 'var(--green)' : isActive ? 'var(--accent-bright)' : 'var(--text-muted)' }}>
                  {isDone ? '✓ Done' : isActive ? '● Active' : '○ Idle'}
                </div>
              </div>

              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 14 }}>
                {agent.description}
              </p>

              <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 6 }}>Tools</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  {agent.tools.map(t => (
                    <span key={t} style={{ padding: '2px 8px', background: 'var(--navy)', border: '1px solid var(--border-subtle)', borderRadius: 4, fontSize: 10, color: 'var(--text-muted)' }}>{t}</span>
                  ))}
                </div>
              </div>

              <div style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between', paddingTop: 10, borderTop: '1px solid var(--border-subtle)' }}>
                <span>Model: <span style={{ color: 'var(--text-secondary)' }}>{agent.model}</span></span>
                {activity?.timestamp && <span>{activity.timestamp.slice(11, 16)}</span>}
              </div>
            </div>
          );
        })}
      </div>

      {/* Competitor assignment table */}
      <div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 12 }}>Research Agent Assignments</div>
        <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                {['Competitor', 'Domain', 'Keywords', 'Articles Collected', 'Status'].map(h => (
                  <th key={h} style={{ padding: '9px 12px', textAlign: 'left', fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {competitors.map((c, i) => (
                <tr 
                  key={i} 
                  style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.15s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--slate)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '10px 12px', fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>{c.name}</td>
                  <td style={{ padding: '10px 12px', fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{c.domain}</td>
                  <td style={{ padding: '10px 12px', fontSize: 11, color: 'var(--text-muted)' }}>{(c.keywords || []).join(', ')}</td>
                  <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-primary)' }}>{c.article_count || 0}</td>
                  <td style={{ padding: '10px 12px' }}>
                    <span style={{ padding: '2px 8px', background: 'rgba(22,163,74,0.15)', color: '#4ade80', borderRadius: 4, fontSize: 10, fontWeight: 600 }}>ACTIVE</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
