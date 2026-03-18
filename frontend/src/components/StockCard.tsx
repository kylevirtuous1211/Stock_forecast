import { useState, useEffect } from 'react'
import { ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react'

interface StockCardProps {
  symbol: string
}

export default function StockCard({ symbol }: StockCardProps) {
  const [data, setData] = useState<any[]>([])
  const [recommendation, setRecommendation] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [orderStatus, setOrderStatus] = useState<string | null>(null)

  useEffect(() => {
    // Fetch price history
    const fetchHistory = fetch('/api/historical', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbols: [symbol], lookback_minutes: 5 })
    }).then(res => res.json())

    // Fetch recommendation
    const fetchRec = fetch(`/api/recommendation?symbol=${symbol}`).then(res => res.json())

    Promise.all([fetchHistory, fetchRec])
      .then(([historyJson, recJson]) => {
        setData(historyJson.data[symbol] || [])
        setRecommendation(recJson)
        setLoading(false)
      })
      .catch(err => console.error(err))
  }, [symbol])

  const handleOrder = () => {
    if (!recommendation) return;
    setOrderStatus('Processing...')
    fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, quantity: 10, side: recommendation.signal.toLowerCase() })
    })
      .then(res => res.json())
      .then(resData => {
        setOrderStatus(resData.message)
        setTimeout(() => setOrderStatus(null), 3000)
      })
  }

  if (loading || data.length === 0) {
    return (
      <div className="glass-card stock-card animate-pulse">
        <div className="stock-symbol">{symbol}</div>
        <div className="stock-price">...</div>
      </div>
    )
  }

  const latest = data[data.length - 1]
  const prev = data[0]
  const change = latest.close - prev.close
  const pctChange = (change / prev.close) * 100
  const isPositive = change >= 0

  return (
    <div className="glass-card stock-card" style={{ position: 'relative', overflow: 'hidden' }}>
      <div className="stock-symbol">{symbol}</div>
      <div className="stock-price">${latest.close.toFixed(2)}</div>
      <div className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
        {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        {Math.abs(pctChange).toFixed(2)}%
        <span style={{ fontSize: '0.75rem', opacity: 0.7, marginLeft: '4px' }}>
          ({isPositive ? '+' : ''}{change.toFixed(2)})
        </span>
      </div>

      {/* Recommendation and Order Section */}
      {recommendation && (
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--glass-border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>AI Signal</span>
            <span style={{ 
              fontWeight: 'bold', 
              color: recommendation.signal === 'BUY' ? 'var(--positive)' : recommendation.signal === 'SELL' ? 'var(--negative)' : '#fbbf24'
            }}>
              {recommendation.signal} ({(recommendation.confidence * 100).toFixed(0)}%)
            </span>
          </div>
          
          {recommendation.signal !== 'HOLD' && (
             <button 
               onClick={handleOrder}
               disabled={!!orderStatus}
               style={{
                 width: '100%',
                 padding: '0.5rem',
                 borderRadius: '0.5rem',
                 border: 'none',
                 background: recommendation.signal === 'BUY' ? 'rgba(74, 222, 128, 0.2)' : 'rgba(248, 113, 113, 0.2)',
                 color: recommendation.signal === 'BUY' ? 'var(--positive)' : 'var(--negative)',
                 fontWeight: 600,
                 cursor: orderStatus ? 'wait' : 'pointer',
                 display: 'flex',
                 alignItems: 'center',
                 justifyContent: 'center',
                 gap: '0.5rem',
                 transition: 'background 0.2s',
               }}
             >
               <Zap size={16} />
               {orderStatus || `Execute Market ${recommendation.signal}`}
             </button>
          )}
        </div>
      )}
    </div>
  )
}
