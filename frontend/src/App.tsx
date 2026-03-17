import { useState, useEffect } from 'react'
import { TrendingUp, RefreshCcw, Activity } from 'lucide-react'
import MarketChart from './components/PerformanceChart'
import StockCard from './components/StockCard'

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
          <h1>Sector Forecast</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Real-time stock monitoring & predictive analytics</p>
        </div>
        <button className="glass-card" style={{ padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }} onClick={() => window.location.reload()}>
          <RefreshCcw size={18} />
          <span>Refresh Data</span>
        </button>
      </header>

      <div className="grid">
        <div className="chart-container glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp className="positive" />
              XLK Performance (Index)
            </h3>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Last 60 Minutes</div>
          </div>
          <MarketChart />
        </div>

        {loading ? (
          Array.from({ length: 11 }).map((_, i) => (
            <div key={i} className="glass-card animate-pulse" style={{ height: '160px' }}></div>
          ))
        ) : (
          symbols.map(symbol => (
            <StockCard key={symbol} symbol={symbol} />
          ))
        )}
      </div>
    </div>
  )
}

export default App
