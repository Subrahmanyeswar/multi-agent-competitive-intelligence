import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { getSignals, getCompetitors } from '../services/api';

export default function SignalGraph({ refreshKey }) {
  const svgRef = useRef(null);
  const [signals, setSignals] = useState({ topic_signals: [], company_momentum: [] });
  const [competitors, setCompetitors] = useState([]);
  const [tooltip, setTooltip] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const [sRes, cRes] = await Promise.all([getSignals(), getCompetitors()]);
        setSignals(sRes.data || {});
        setCompetitors(cRes.data.competitors || []);
      } catch(e) {}
      setLoading(false);
    };
    fetch();
  }, [refreshKey]);

  useEffect(() => {
    if (loading || !svgRef.current) return;
    buildGraph();
  }, [signals, competitors, loading]);

  const buildGraph = () => {
    const container = svgRef.current.parentElement;
    const W = container.offsetWidth;
    const H = 480;

    d3.select(svgRef.current).selectAll('*').remove();

    const nodes = [];
    const links = [];

    // Company nodes
    competitors.forEach(c => {
      nodes.push({ id: c.name, type: 'company', label: c.name, value: (c.article_count || 1) * 2 });
    });

    // Topic nodes and links
    (signals.topic_signals || []).forEach(sig => {
      const topicId = `topic_${sig.topic}`;
      nodes.push({
        id: topicId,
        type: sig.composite_score > 0.6 ? 'hot_signal' : 'signal',
        label: sig.topic?.replace(/_/g, ' '),
        value: Math.round((sig.composite_score || 0) * 30) + 8,
        score: sig.composite_score,
        velocity: sig.velocity,
      });
      (sig.companies_involved || []).forEach(company => {
        if (nodes.find(n => n.id === company)) {
          links.push({ source: company, target: topicId, strength: sig.composite_score || 0.1 });
        }
      });
    });

    const nodeColors = {
      company: '#2563eb',
      signal: '#0d9488',
      hot_signal: '#d97706',
    };

    const svg = d3.select(svgRef.current)
      .attr('width', W).attr('height', H);

    svg.append('rect').attr('width', W).attr('height', H).attr('fill', '#0a0f1e').attr('rx', 8);

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(d => 120 - d.strength * 40).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(W / 2, H / 2))
      .force('collision', d3.forceCollide(d => (d.value || 10) + 12));

    const link = svg.append('g').selectAll('line').data(links).join('line')
      .attr('stroke', '#1e3a5f')
      .attr('stroke-width', d => Math.max(1, d.strength * 3))
      .attr('stroke-opacity', 0.6);

    const node = svg.append('g').selectAll('g').data(nodes).join('g')
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    node.append('circle')
      .attr('r', d => d.value || 10)
      .attr('fill', d => nodeColors[d.type] + '30')
      .attr('stroke', d => nodeColors[d.type])
      .attr('stroke-width', 1.5);

    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('fill', '#f1f5f9')
      .attr('font-size', d => d.type === 'company' ? 11 : 10)
      .attr('font-weight', d => d.type === 'company' ? 600 : 400)
      .attr('font-family', 'DM Sans, sans-serif')
      .text(d => d.label?.length > 12 ? d.label.slice(0, 12) + '…' : d.label);

    node.on('mouseover', (event, d) => {
      setTooltip({
        x: event.clientX,
        y: event.clientY,
        data: d,
      });
      d3.select(event.currentTarget).select('circle').attr('stroke-width', 2.5);
    }).on('mouseout', (event) => {
      setTooltip(null);
      d3.select(event.currentTarget).select('circle').attr('stroke-width', 1.5);
    });

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${Math.max(20, Math.min(W - 20, d.x))},${Math.max(20, Math.min(H - 20, d.y))})`);
    });

    // Legend
    const legend = svg.append('g').attr('transform', 'translate(16, 16)');
    [
      { color: '#2563eb', label: 'Company' },
      { color: '#0d9488', label: 'Signal topic' },
      { color: '#d97706', label: 'High-velocity signal' },
    ].forEach(({ color, label }, i) => {
      legend.append('circle').attr('cx', 8).attr('cy', i * 22 + 8).attr('r', 6).attr('fill', color + '40').attr('stroke', color).attr('stroke-width', 1.5);
      legend.append('text').attr('x', 20).attr('y', i * 22 + 13).attr('fill', '#94a3b8').attr('font-size', 11).attr('font-family', 'DM Sans, sans-serif').text(label);
    });
  };

  return (
    <div style={{ maxWidth: 1100 }}>
      <div style={{ position: 'relative', background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 10, overflow: 'hidden', marginBottom: 24 }}>
        <svg ref={svgRef} style={{ display: 'block', width: '100%' }} />
        {loading && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(10,15,30,0.8)', fontSize: 13, color: 'var(--text-muted)' }}>
            Loading signal graph...
          </div>
        )}
        {!loading && (signals.topic_signals || []).length === 0 && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(10,15,30,0.8)', fontSize: 13, color: 'var(--text-muted)' }}>
            No signal data — run the pipeline first
          </div>
        )}
      </div>

      {tooltip && (
        <div style={{
          position: 'fixed', left: tooltip.x + 12, top: tooltip.y - 40,
          background: '#111827', border: '1px solid var(--border)',
          borderRadius: 6, padding: '8px 12px', fontSize: 12,
          color: 'var(--text-primary)', pointerEvents: 'none', zIndex: 1000,
          maxWidth: 200,
        }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>{tooltip.data.label}</div>
          <div style={{ color: 'var(--text-muted)' }}>Type: {tooltip.data.type?.replace(/_/g, ' ')}</div>
          {tooltip.data.score !== undefined && <div style={{ color: 'var(--text-muted)' }}>Score: {Math.round(tooltip.data.score * 100)}%</div>}
          {tooltip.data.velocity !== undefined && <div style={{ color: 'var(--text-muted)' }}>Velocity: {(tooltip.data.velocity || 0).toFixed(1)}x</div>}
        </div>
      )}

      {/* Signal table */}
      <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-subtle)', fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>Signal Strength Table</div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              {['Topic', 'Velocity', 'Spread', 'Composite Score', 'Strength', 'Companies'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(signals.topic_signals || []).map((sig, i) => {
              const pct = Math.round((sig.composite_score || 0) * 100);
              const color = pct > 60 ? '#dc2626' : pct > 30 ? '#d97706' : '#2563eb';
              return (
                <tr 
                  key={i} 
                  style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.15s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--slate)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '9px 12px', fontSize: 13, color: 'var(--text-primary)', textTransform: 'capitalize' }}>{sig.topic?.replace(/_/g, ' ')}</td>
                  <td style={{ padding: '9px 12px', fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>{(sig.velocity || 0).toFixed(1)}x</td>
                  <td style={{ padding: '9px 12px', fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>{sig.source_spread || 0}</td>
                  <td style={{ padding: '9px 12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ flex: 1, height: 4, background: 'var(--navy)', borderRadius: 2, overflow: 'hidden', maxWidth: 80 }}>
                        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 2 }} />
                      </div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color }}>{pct}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '9px 12px' }}>
                    <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 10, fontWeight: 600, color: '#fff', background: color }}>
                      {sig.signal_strength?.toUpperCase() || 'WEAK'}
                    </span>
                  </td>
                  <td style={{ padding: '9px 12px', fontSize: 11, color: 'var(--text-muted)' }}>{(sig.companies_involved || []).join(', ')}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
