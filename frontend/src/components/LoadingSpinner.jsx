import { Loader2 } from 'lucide-react'

const LoadingSpinner = ({ text = 'Загрузка...' }) => {
  return (
    <div className="glass-card p-12 flex flex-col items-center gap-4">
      <Loader2 size={48} className="animate-spin text-accent-cyan" />
      <p className="text-text-secondary">{text}</p>
    </div>
  )
}

export default LoadingSpinner
