export const Skeleton = ({ width = '100%', height = 16, style }) => (
  <div style={{
    width, height,
    background: 'linear-gradient(90deg, var(--navy-2) 25%, var(--slate) 50%, var(--navy-2) 75%)',
    backgroundSize: '200% 100%',
    animation: 'shimmer 1.5s infinite',
    borderRadius: 4,
    ...style,
  }}>
    <style>{`@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }`}</style>
  </div>
);

export const CardSkeleton = () => (
  <div style={{ background: 'var(--navy-2)', border: '1px solid var(--border-subtle)', borderRadius: 8, padding: '16px 18px' }}>
    <Skeleton height={12} width="60%" style={{ marginBottom: 12 }} />
    <Skeleton height={28} width="40%" />
  </div>
);
