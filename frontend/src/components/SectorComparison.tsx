import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts'
import { BarChart3 } from 'lucide-react'

export default function SectorComparison() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // In a real scenario, this would be a dedicated endpoint or calculated from historical data
    // Here we simulate the relative strength based on mock data
    
    const mockData = [
      { name: 'NVDA', rs: 2.4 },
      { name: 'AMD', rs: 1.8 },
      { name: 'MSFT', rs: 0.5 },
      { name: 'AAPL', rs: -0.2 },
      { name: 'CRM', rs: -1.5 },
    ]
    setData(mockData)
    setLoading(false)
  }, [])

  if (loading) {
     return <div className="glass-card animate-pulse" style={{ height: '240px' }} />
  }

  return (
    <div className="glass-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
       <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
         <BarChart3 size={18} color="var(--accent-color)" />
         <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Sector Relative Strength</h3>
      </div>
      
      <div style={{ flex: 1, minHeight: 180 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 30, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={true} vertical={false} />
            <XAxis type="number" stroke="var(--text-secondary)" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis 
               dataKey="name" 
               type="category" 
               stroke="var(--text-secondary)" 
               fontSize={12} 
               tickLine={false} 
               axisLine={false}
               width={50}
            />
            <Tooltip 
               cursor={{ fill: 'rgba(255,255,255,0.05)' }}
               contentStyle={{ 
                 backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                 border: '1px solid var(--glass-border)',
                 borderRadius: '8px',
               }}
            />
            <ReferenceLine x={0} stroke="var(--text-secondary)" strokeOpacity={0.5} />
            <Bar dataKey="rs" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.rs >= 0 ? 'var(--positive)' : 'var(--negative)'} fillOpacity={entry.rs >= 0 ? 0.8 : 0.6} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
