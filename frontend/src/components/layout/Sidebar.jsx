import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Radio, Database, FileText,
  TrendingUp, Settings, Activity, GitBranch
} from 'lucide-react';

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/pipeline', icon: Radio, label: 'Live Pipeline' },
  { to: '/agents', icon: Activity, label: 'Agent Activity' },
  { to: '/intelligence', icon: TrendingUp, label: 'Intelligence' },
  { to: '/graph', icon: GitBranch, label: 'Signal Graph' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/data', icon: Database, label: 'Data Store' },
];

export default function Sidebar() {
  return (
    <aside style={{
      width: 220,
      minHeight: '100vh',
      background: 'var(--navy-2)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      <div style={{
        padding: '24px 20px 20px',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28, height: 28,
            background: 'var(--accent)',
            borderRadius: 6,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Activity size={14} color="#fff" />
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '0.02em' }}>
              Intel
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Competitive AI
            </div>
          </div>
        </div>
      </div>

      <nav style={{ flex: 1, padding: '12px 10px' }}>
        {nav.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === '/'} style={({ isActive }) => ({
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '8px 12px',
            borderRadius: 8,
            marginBottom: 2,
            textDecoration: 'none',
            fontSize: 13,
            fontWeight: isActive ? 500 : 400,
            color: isActive ? 'var(--accent-bright)' : 'var(--text-secondary)',
            background: isActive ? 'var(--accent-glow)' : 'transparent',
            border: isActive ? '1px solid rgba(59,130,246,0.2)' : '1px solid transparent',
            transition: 'all 0.15s ease',
          })}>
            <Icon size={15} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: 11,
        color: 'var(--text-muted)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{
            width: 6, height: 6, borderRadius: '50%',
            background: 'var(--green)',
            boxShadow: '0 0 6px var(--green)',
          }} />
          System active
        </div>
        <div style={{ marginTop: 4 }}>Mistral AI + Qdrant</div>
      </div>
    </aside>
  );
}
