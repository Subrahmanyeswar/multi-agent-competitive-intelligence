import { useEffect, useState } from 'react';
import { getArticles, getVectorStats, getCompetitors } from '../services/api';
import { Database, ExternalLink, Search } from 'lucide-react';
import { format, parseISO } from 'date-fns';

export default function DataStore({ refreshKey }) {
  const [articles, setArticles] = useState([]);
  const [vectorStats, setVectorStats] = useState({});
  const [competitors, setCompetitors] = useState([]);
  const [filter, setFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const [aRes, vRes, cRes] = await Promise.all([getArticles(), getVectorStats(), getCompetitors()]);
        setArticles(aRes.data.articles || []);
        setVectorStats(vRes.data || {});
        setCompetitors(cRes.data.competitors || []);
      } catch(e) {}
      setLoading(false);
    };
    fetch();
  }, [refreshKey]);

  const filtered = articles.filter(a => {
    const matchCompany = !filter || a.company === filter;
    const matchSearch = !search || (a.title || '').toLowerCase().includes(search.toLowerCase());
    return matchCompany && matchSearch;
  });

  const stats = [
    { label: 'Total Articles', value: articles.length },
    { label: 'Vectors Stored', value: vectorStats.vectors_count > 0 ? vectorStats.vectors_count : '—' },
    { label: 'Collection', value: vectorStats.collection || 'competitor_news' },
    { label: 'DB Status', value: vectorStats.status || '—' },
  ];

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Vector DB stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
        {stats.map(({ label, value }) => (
          <div key={label} style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: '14px 16px' }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>{label}</div>
            <div style={{ fontSize: 20, fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>{typeof value === 'number' ? value.toLocaleString() : value}</div>
            {label === 'Vectors Stored' && vectorStats.vectors_count === 0 && (
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                Updates after pipeline run
              </div>
            )}
          </div>
        ))}
      </div>

      <div style={{
        padding: '10px 14px', marginBottom: 16,
        background: 'rgba(37,99,235,0.08)', border: '1px solid rgba(59,130,246,0.2)',
        borderRadius: 6, fontSize: 12, color: 'var(--text-secondary)',
        lineHeight: 1.6,
      }}>
        Articles are collected from TechCrunch, Reuters, Bloomberg, and The Verge 
        based on competitor keywords. Some adjacent company names (Apple, Nvidia) 
        may appear when they are mentioned in the same AI industry articles. 
        Use the company filter to view only specific competitor data.
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            placeholder="Search articles..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              width: '100%', padding: '8px 12px 8px 30px',
              background: 'var(--navy-2)', border: '1px solid var(--border-subtle)',
              borderRadius: 6, color: 'var(--text-primary)', fontSize: 13,
              outline: 'none',
            }}
          />
        </div>
        <select
          value={filter}
          onChange={e => setFilter(e.target.value)}
          style={{
            padding: '8px 12px', background: 'var(--navy-2)',
            border: '1px solid var(--border-subtle)', borderRadius: 6,
            color: 'var(--text-primary)', fontSize: 13, cursor: 'pointer',
          }}
        >
          <option value="">All companies</option>
          {competitors.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
        </select>
      </div>

      {/* Articles table */}
      <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Article Store</span>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{filtered.length} records</span>
        </div>
        <div style={{ maxHeight: 520, overflowY: 'auto' }}>
          {loading ? (
            <div style={{ padding: 20, fontSize: 13, color: 'var(--text-muted)' }}>Loading...</div>
          ) : filtered.length === 0 ? (
            <div style={{ padding: 20, fontSize: 13, color: 'var(--text-muted)' }}>No articles found. Run the pipeline to collect data.</div>
          ) : (
            filtered.map((article, i) => (
              <div 
                key={i} 
                style={{ padding: '12px 14px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'flex-start', gap: 14, transition: 'background 0.15s' }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--slate)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 10, fontWeight: 600, background: 'rgba(13,148,136,0.15)', color: '#2dd4bf', flexShrink: 0, marginTop: 2 }}>
                  {article.company || '—'}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, color: 'var(--text-primary)', marginBottom: 3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {article.title || 'Untitled'}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', gap: 12 }}>
                    <span>{article.source || '—'}</span>
                    <span>{article.stored_at ? format(parseISO(article.stored_at), 'MMM d, HH:mm') : ''}</span>
                  </div>
                </div>
                {article.url && (
                  <a href={article.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: 2 }}>
                    <ExternalLink size={13} />
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
