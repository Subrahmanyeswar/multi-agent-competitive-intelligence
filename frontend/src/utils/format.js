export const fmtNumber = (n) => typeof n === 'number' ? n.toLocaleString() : (n || '—');
export const fmtPct = (n) => typeof n === 'number' ? `${Math.round(n * 100)}%` : '—';
export const fmtMono = (n, decimals = 1) => typeof n === 'number' ? n.toFixed(decimals) : '—';
