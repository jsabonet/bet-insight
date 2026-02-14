import { useEffect, useState } from 'react';
import { matchesAPI } from '../services/api';

export default function TestQuickAnalyze() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const run = async () => {
      try {
        const payload = {
          home_team: 'Rennes',
          away_team: 'Paris Saint Germain',
          league: 'Ligue 1',
          date: '2026-02-13T18:00:00Z',
          api_id: 1387895,
          strategy: 'value',
          skip_ai: true
        };
        const res = await matchesAPI.quickAnalyze(payload);
        setData(res.data);
      } catch (e) {
        setError(String(e?.response?.data?.error || e.message));
      }
    };
    run();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>Frontend Quick Analyze Test</h1>
      {error && <div style={{ color: 'red' }}>Error: {error}</div>}
      {!data && !error && <div>Loading…</div>}
      {data && (
        <div>
          <h2>Top Bets</h2>
          <ul>
            {(data.top_bets || []).map((b) => (
              <li key={b.rank}>
                #{b.rank} {b.market_display} — Prob {Math.round(b.probability * 100)}% — Odd {b.market_odd} — EV {b.ev_pct.toFixed(1)}%
              </li>
            ))}
          </ul>
          <h2>Context Patterns</h2>
          <ul>
            {(data.context_analysis?.patterns || []).map((p, i) => (
              <li key={i}>
                {p.name} — conf {Math.round(p.confidence * 100)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
