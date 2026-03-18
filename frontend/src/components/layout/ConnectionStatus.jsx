import { useEffect, useState } from 'react';
import { getPipelineStatus } from '../../services/api';
import { WifiOff } from 'lucide-react';

export default function ConnectionStatus() {
  const [connected, setConnected] = useState(true);

  useEffect(() => {
    const check = async () => {
      try {
        await getPipelineStatus();
        setConnected(true);
      } catch {
        setConnected(false);
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  if (connected) return null;

  return (
    <div style={{
      background: '#450a0a', border: '1px solid #991b1b',
      padding: '10px 20px', display: 'flex', alignItems: 'center', gap: 8,
      fontSize: 12, color: '#fca5a5',
    }}>
      <WifiOff size={13} />
      Backend API not reachable — make sure api_server.py is running on port 8000
    </div>
  );
}
