import { useState, useEffect } from 'react'
import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

interface StockCardProps {
  symbol: string
}

export default function StockCard({ symbol }: StockCardProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/historical', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbols: [symbol], lookback_minutes: 5 })
    })
    .then(res => res.json())
    .then(json => {
      setData(json.data[symbol] || [])
      setLoading(false)
    })
    .catch(err => console.error(err))
  }, [symbol])

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
    <div className="glass-card stock-card">
      <div className="stock-symbol">{symbol}</div>
      <div className="stock-price">${latest.close.toFixed(2)}</div>
      <div className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
        {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        {Math.abs(pctChange).toFixed(2)}%
        <span style={{ fontSize: '0.75rem', opacity: 0.7, marginLeft: '4px' }}>
          ({isPositive ? '+' : ''}{change.toFixed(2)})
        </span>
      </div>
    </div>
  )
}
