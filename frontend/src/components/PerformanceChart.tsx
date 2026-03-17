import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

export default function PerformanceChart() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/index-performance?lookback_minutes=60')
      .then(res => res.json())
      .then(json => {
        const formattedData = json.data.map((item: any) => ({
          time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          price: item.close,
          timestamp: item.timestamp
        }))
        setData(formattedData)
        setLoading(false)
      })
      .catch(err => console.error(err))
  }, [])

  if (loading || data.length === 0) {
    return (
      <div className="loading animate-pulse" style={{ height: '300px' }}>
        <p>Analyzing Market Data...</p>
      </div>
    )
  }

  // Calculate stats
  const firstPrice = data[0].price
  const lastPrice = data[data.length - 1].price
  const isPositive = lastPrice >= firstPrice

  return (
    <div style={{ width: '100%', height: 350 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={isPositive ? "#4ade80" : "#f87171"} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={isPositive ? "#4ade80" : "#f87171"} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
          <XAxis 
            dataKey="time" 
            stroke="var(--text-secondary)" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis 
            stroke="var(--text-secondary)" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            domain={['auto', 'auto']}
            tickFormatter={(value) => `$${value.toFixed(0)}`}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(15, 23, 42, 0.9)', 
              border: '1px solid var(--glass-border)',
              borderRadius: '8px',
              backdropFilter: 'blur(4px)'
            }}
            itemStyle={{ color: 'var(--text-primary)' }}
          />
          <Area 
            type="monotone" 
            dataKey="price" 
            stroke={isPositive ? "#4ade80" : "#f87171"} 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorPrice)" 
            animationDuration={1500}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
