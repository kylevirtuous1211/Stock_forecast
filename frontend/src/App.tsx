import { useState, useEffect } from 'react'
import { TrendingUp, RefreshCcw, Activity } from 'lucide-react'
import PerformanceChart from './components/PerformanceChart'
import StockCard from './components/StockCard'
import RetrainButton from './components/RetrainButton'
import ConfidenceGauge from './components/ConfidenceGauge'
import SectorComparison from './components/SectorComparison'

function App() {
  const [symbols, setSymbols] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/tracked-stocks')
      .then(res => res.json())
      .then(data => {
        setSymbols(data)
        setLoading(false)
      })
      .catch(err => console.error('Failed to fetch stocks:', err))
  }, [])

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>Sector Forecast AI</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Real-time execution & predictive analytics</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <RetrainButton />
          <button className="glass-card" style={{ padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }} onClick={() => window.location.reload()}>
            <RefreshCcw size={18} />
          </button>
        </div>
      </header>

      {/* Top Section: Charts and Analytics */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '1.5rem', marginBottom: '1.5rem' }}>
         <div className="glass-card" style={{ minHeight: '400px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <TrendingUp className="positive" />
                XLK Index Performance
              </h3>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Live Feed (15m delay)</div>
            </div>
            <PerformanceChart />
         </div>

         <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
             <ConfidenceGauge confidence={0.84} />
             <SectorComparison />
         </div>
      </div>

      {/* Bottom Section: Stock Grid */}
      <div>
        <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity color="var(--accent-color)" />
            Tracked Assets & Signals
        </h2>
        <div className="grid">
          {loading ? (
            Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="glass-card animate-pulse" style={{ height: '220px' }}></div>
            ))
          ) : (
            symbols.map(symbol => (
              <StockCard key={symbol} symbol={symbol} />
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default App
