import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { Activity } from 'lucide-react'

// Simple implementation of a custom Needle
const RADIAN = Math.PI / 180;
const data = [
  { name: 'Low', value: 33, color: '#f87171' },
  { name: 'Medium', value: 33, color: '#fbbf24' },
  { name: 'High', value: 34, color: '#4ade80' },
];

const needle = (value: number, data: any[], cx: number, cy: number, iR: number, oR: number, color: string) => {
  let total = 0;
  data.forEach((v) => {
    total += v.value;
  });
  // scale value from 0-1 to 0-total
  const scaledValue = value * total;
  const ang = 180.0 * (1 - scaledValue / total);
  
  const length = (iR + 2 * oR) / 3;
  const sin = Math.sin(-RADIAN * ang);
  const cos = Math.cos(-RADIAN * ang);
  const r = 5;
  const x0 = cx + 5;
  const y0 = cy + 5;
  const xba = x0 + r * sin;
  const yba = y0 - r * cos;
  const xbb = x0 - r * sin;
  const ybb = y0 + r * cos;
  const xp = x0 + length * cos;
  const yp = y0 + length * sin;

  return [
    <path key="needle" d={`M${xba} ${yba}L${xbb} ${ybb} L${xp} ${yp} L${xba} ${yba}`} stroke="none" fill={color} />,
    <circle key="center" cx={x0} cy={y0} r={r} fill={color} stroke="none" />,
  ];
};

export default function ConfidenceGauge({ confidence }: { confidence: number }) {
  // confidence comes in as a float e.g 0.85
  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
         <Activity size={18} color="var(--accent-color)" />
         <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Model Confidence</h3>
      </div>
      <div style={{ flex: 1, minHeight: 180, position: 'relative' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              dataKey="value"
              startAngle={180}
              endAngle={0}
              data={data}
              cx="50%"
              cy="75%"
              innerRadius={60}
              outerRadius={80}
              fill="#8884d8"
              stroke="none"
              paddingAngle={2}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} opacity={0.8} />
              ))}
            </Pie>
            {/* The needle render is slightly manual in recharts */}
            {(() => {
                const cx = 140; // Approx center
                const cy = 125;
                const iR = 60;
                const oR = 80;
                return needle(confidence, data, cx, cy, iR, oR, '#f8fafc');
            })()}
          </PieChart>
        </ResponsiveContainer>
        <div style={{ position: 'absolute', bottom: '10px', width: '100%', textAlign: 'center' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{(confidence * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  )
}
