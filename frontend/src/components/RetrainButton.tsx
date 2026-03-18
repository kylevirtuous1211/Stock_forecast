import { useState, useEffect } from 'react'
import { RefreshCw } from 'lucide-react'

export default function RetrainButton() {
  const [status, setStatus] = useState<any>({ is_training: false, progress: 0, message: "Idle" })
  const [isHovered, setIsHovered] = useState(false)

  // Poll status if training is active
  useEffect(() => {
    let interval: any;
    if (status.is_training) {
      interval = setInterval(() => {
        fetch('/api/train-status')
          .then(res => res.json())
          .then(data => {
            setStatus(data)
            if (!data.is_training) {
              clearInterval(interval)
            }
          })
      }, 3000)
    }
    return () => clearInterval(interval)
  }, [status.is_training])

  const handleRetrain = () => {
    if (status.is_training) return;
    
    fetch('/api/retrain', { method: 'POST' })
      .then(res => res.json())
      .then(() => {
        // Optimistically set status to trigger polling
        setStatus({ ...status, is_training: true, message: "Initializing..." })
      })
  }

  return (
    <div className="glass-card" style={{ flex: 1 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.2rem' }}>Model Management</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '4px' }}>
            {status.is_training ? status.message : "Model is up to date and ready for inference."}
          </p>
        </div>
        
        <button 
          onClick={handleRetrain}
          disabled={status.is_training}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{
            background: status.is_training ? 'rgba(255,255,255,0.1)' : (isHovered ? 'var(--accent-color)' : 'rgba(56, 189, 248, 0.2)'),
            color: isHovered && !status.is_training ? '#0f172a' : 'var(--accent-color)',
            border: `1px solid ${status.is_training ? 'transparent' : 'var(--accent-color)'}`,
            padding: '0.75rem 1.5rem',
            borderRadius: '0.75rem',
            cursor: status.is_training ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontWeight: 600,
            transition: 'all 0.2s'
          }}
        >
          <RefreshCw size={18} className={status.is_training ? "animate-spin" : ""} />
          {status.is_training ? 'Training Active' : 'Retrain Model'}
        </button>
      </div>

      {status.is_training && (
        <div style={{ marginTop: '1.5rem', background: 'rgba(0,0,0,0.2)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
          <div 
            style={{ 
              height: '100%', 
              width: `${status.progress}%`, 
              background: 'linear-gradient(90deg, var(--accent-color), #818cf8)',
              transition: 'width 0.5s ease-in-out'
            }} 
          />
        </div>
      )}
    </div>
  )
}
