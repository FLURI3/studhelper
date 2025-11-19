import { useState, useEffect } from 'react'
import { Brain, Zap, TrendingUp, Download, Upload, CheckCircle, AlertCircle, Info, Loader2 } from 'lucide-react'
import axios from 'axios'

const Training = () => {
  const [trainingStats, setTrainingStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [manualExamples, setManualExamples] = useState([])
  const [newExample, setNewExample] = useState({
    original: '',
    summary: '',
    ratio: 50
  })
  const [message, setMessage] = useState(null)
  const [trainingStatus, setTrainingStatus] = useState(null)
  const [isTrainingInProgress, setIsTrainingInProgress] = useState(false)

  useEffect(() => {
    fetchTrainingStats()
    loadManualExamples()
    
    const interval = setInterval(fetchTrainingStats, 10000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (isTrainingInProgress) {
      const statusInterval = setInterval(fetchTrainingStatus, 2000)
      return () => clearInterval(statusInterval)
    }
  }, [isTrainingInProgress])

  const fetchTrainingStatus = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/training/status`
      )
      setTrainingStatus(response.data)
      
      if (!response.data.is_training && isTrainingInProgress) {
        setIsTrainingInProgress(false)
        setLoading(false)
        fetchTrainingStats() // Обновляем статистику после завершения
        
        if (response.data.error) {
          setMessage({ type: 'error', text: `Ошибка обучения: ${response.data.error}` })
        } else if (response.data.progress === 100) {
          setMessage({ type: 'success', text: `Модель ${response.data.model_name} готова!` })
        }
      }
    } catch (error) {
      console.error('Error fetching training status:', error)
    }
  }

  const fetchTrainingStats = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/training/stats`
      )
      setTrainingStats(response.data)
    } catch (error) {
      console.error('Error fetching training stats:', error)
    }
  }

  const loadManualExamples = () => {
    try {
      const saved = localStorage.getItem('training_examples')
      if (saved) {
        setManualExamples(JSON.parse(saved))
      }
    } catch (error) {
      console.error('Error loading examples:', error)
    }
  }

  const saveManualExamples = (examples) => {
    try {
      localStorage.setItem('training_examples', JSON.stringify(examples))
      setManualExamples(examples)
    } catch (error) {
      console.error('Error saving examples:', error)
    }
  }

  const addExample = () => {
    if (!newExample.original.trim() || !newExample.summary.trim()) {
      setMessage({ type: 'error', text: 'Заполните оба текста!' })
      return
    }

    const examples = [...manualExamples, { ...newExample, id: Date.now() }]
    saveManualExamples(examples)
    
    setNewExample({ original: '', summary: '', ratio: 50 })
    setMessage({ type: 'success', text: 'Пример добавлен!' })
    
    setTimeout(() => setMessage(null), 3000)
  }

  const deleteExample = (id) => {
    const examples = manualExamples.filter(ex => ex.id !== id)
    saveManualExamples(examples)
    setMessage({ type: 'success', text: 'Пример удалён!' })
    setTimeout(() => setMessage(null), 3000)
  }

  const exportExamples = () => {
    const data = JSON.stringify(manualExamples.map(ex => ({
      original: ex.original,
      summary: ex.summary,
      ratio: ex.ratio
    })), null, 2)
    
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'training_examples.json'
    a.click()
    URL.revokeObjectURL(url)
    
    setMessage({ type: 'success', text: 'Примеры экспортированы!' })
    setTimeout(() => setMessage(null), 3000)
  }

  const importExamples = (event) => {
    const file = event.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target.result)
        const withIds = imported.map(ex => ({ ...ex, id: Date.now() + Math.random() }))
        saveManualExamples([...manualExamples, ...withIds])
        setMessage({ type: 'success', text: `Импортировано ${imported.length} примеров!` })
        setTimeout(() => setMessage(null), 3000)
      } catch (error) {
        setMessage({ type: 'error', text: 'Ошибка импорта файла!' })
        setTimeout(() => setMessage(null), 3000)
      }
    }
    reader.readAsText(file)
  }

  const startTraining = async () => {
    if (manualExamples.length < 5) {
      setMessage({ type: 'error', text: 'Добавьте минимум 5 примеров для обучения!' })
      setTimeout(() => setMessage(null), 3000)
      return
    }

    setLoading(true)
    setIsTrainingInProgress(true)
    setMessage({ type: 'info', text: 'Запуск обучения... Это займёт 5-10 минут.' })

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/training/start`,
        {
          examples: manualExamples.map(ex => ({
            original: ex.original,
            summary: ex.summary,
            ratio: ex.ratio
          }))
        }
      )
      
      if (response.data.error) {
        setMessage({ type: 'error', text: response.data.error })
        setLoading(false)
        setIsTrainingInProgress(false)
      } else {
        setMessage({ type: 'info', text: 'Обучение началось! Следите за прогрессом ниже.' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Ошибка запуска обучения!' })
      setLoading(false)
      setIsTrainingInProgress(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">🎓 Помощь в обучении модели</h1>
        <p className="text-text-secondary">
          Добавляйте примеры качественного сокращения текста для улучшения работы ИИ
        </p>
      </div>

      {/* Сообщения */}
      {message && (
        <div className={`glass-card p-4 flex items-center gap-3 border-l-4 ${
          message.type === 'success' ? 'border-green-500' :
          message.type === 'error' ? 'border-red-500' :
          'border-accent-cyan'
        }`}>
          {message.type === 'success' && <CheckCircle size={20} className="text-green-500" />}
          {message.type === 'error' && <AlertCircle size={20} className="text-red-500" />}
          {message.type === 'info' && <Info size={20} className="text-accent-cyan" />}
          <p className="flex-1">{message.text}</p>
        </div>
      )}

      {/* Статистика */}
      {trainingStats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-2">
              <Brain className="text-accent-cyan" size={24} />
              <h3 className="font-semibold">Всего примеров</h3>
            </div>
            <p className="text-3xl font-bold">{trainingStats.total_examples}</p>
            <p className="text-sm text-text-secondary mt-1">
              Ручных: {manualExamples.length} | Авто: {trainingStats.auto_collected}
            </p>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="text-accent-cyan" size={24} />
              <h3 className="font-semibold">Прогресс</h3>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">{trainingStats.current_progress}</span>
              <span className="text-text-secondary">/ {trainingStats.auto_train_threshold}</span>
            </div>
            <div className="mt-3 relative h-2 bg-primary-tertiary rounded-full overflow-hidden">
              <div
                className="h-full bg-accent-cyan transition-all duration-300"
                style={{ width: `${trainingStats.progress_percentage}%` }}
              />
            </div>
          </div>

          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-2">
              <Zap className="text-accent-cyan" size={24} />
              <h3 className="font-semibold">Обученные модели</h3>
            </div>
            <p className="text-3xl font-bold">{trainingStats.trained_models.length}</p>
            <p className="text-sm text-text-secondary mt-1">
              {trainingStats.latest_model || 'Нет обученных моделей'}
            </p>
          </div>
        </div>
      )}

      {/* Форма добавления примера */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <CheckCircle size={20} className="text-accent-cyan" />
          Добавить пример для обучения
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Исходный текст (длинный)
            </label>
            <textarea
              value={newExample.original}
              onChange={(e) => setNewExample({ ...newExample, original: e.target.value })}
              className="input-field min-h-[120px] font-mono text-sm"
              placeholder="Введите длинный текст, который нужно сократить..."
            />
            <p className="text-xs text-text-secondary mt-1">
              {newExample.original.length} символов
            </p>
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Сокращённая версия (короткий)
            </label>
            <textarea
              value={newExample.summary}
              onChange={(e) => setNewExample({ ...newExample, summary: e.target.value })}
              className="input-field min-h-[120px] font-mono text-sm"
              placeholder="Введите сокращённую версию текста..."
            />
            <p className="text-xs text-text-secondary mt-1">
              {newExample.summary.length} символов
              {newExample.original.length > 0 && (
                <span className="ml-2 text-accent-cyan">
                  (сжатие {Math.round(newExample.summary.length / newExample.original.length * 100)}%)
                </span>
              )}
            </p>
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Целевой процент сокращения: {newExample.ratio}%
            </label>
            <input
              type="range"
              min="10"
              max="80"
              value={newExample.ratio}
              onChange={(e) => setNewExample({ ...newExample, ratio: Number(e.target.value) })}
              className="w-full h-2 bg-primary-tertiary rounded-lg appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, #00d9ff 0%, #00d9ff ${(newExample.ratio - 10) / 0.7}%, #2d2d2d ${(newExample.ratio - 10) / 0.7}%, #2d2d2d 100%)`
              }}
            />
          </div>

          <button
            onClick={addExample}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            <CheckCircle size={20} />
            <span>Добавить пример</span>
          </button>
        </div>
      </div>

      {/* Список примеров */}
      {manualExamples.length > 0 && (
        <div className="glass-card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">
              Ваши примеры ({manualExamples.length})
            </h2>
            <div className="flex gap-2">
              <label className="btn-secondary cursor-pointer flex items-center gap-2">
                <Upload size={16} />
                <span className="text-sm">Импорт</span>
                <input
                  type="file"
                  accept=".json"
                  onChange={importExamples}
                  className="hidden"
                />
              </label>
              <button
                onClick={exportExamples}
                className="btn-secondary flex items-center gap-2"
              >
                <Download size={16} />
                <span className="text-sm">Экспорт</span>
              </button>
            </div>
          </div>

          <div className="space-y-3 max-h-[400px] overflow-y-auto">
            {manualExamples.map((example) => (
              <div key={example.id} className="p-4 bg-primary-tertiary rounded border border-border">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs text-accent-cyan font-semibold">
                    Сокращение до {example.ratio}%
                  </span>
                  <button
                    onClick={() => deleteExample(example.id)}
                    className="text-xs text-red-500 hover:text-red-400"
                  >
                    Удалить
                  </button>
                </div>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-text-secondary text-xs">Исходный:</span>
                    <p className="mt-1 text-text-primary line-clamp-2 font-mono">
                      {example.original}
                    </p>
                    <span className="text-xs text-text-secondary">
                      {example.original.length} символов
                    </span>
                  </div>
                  <div>
                    <span className="text-text-secondary text-xs">Сокращённый:</span>
                    <p className="mt-1 text-text-primary line-clamp-2 font-mono">
                      {example.summary}
                    </p>
                    <span className="text-xs text-text-secondary">
                      {example.summary.length} символов
                      <span className="ml-2 text-accent-cyan">
                        (фактически {Math.round(example.summary.length / example.original.length * 100)}%)
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Действия */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold">Запуск обучения</h2>
        
        <div className="space-y-3">
          <div className="p-4 bg-primary-tertiary rounded border-l-4 border-accent-cyan">
            <p className="text-sm mb-2">
              <strong>Автоматический режим (рекомендуется):</strong>
            </p>
            <p className="text-sm text-text-secondary mb-3">
              Запустите приложение с автообучением. Модель будет тренироваться автоматически 
              каждые {trainingStats?.auto_train_threshold || 20} примеров.
            </p>
            <code className="block p-2 bg-primary-secondary rounded text-xs font-mono">
              start_auto_learning.bat
            </code>
          </div>

          <div className="p-4 bg-primary-tertiary rounded border-l-4 border-yellow-500">
            <p className="text-sm mb-2">
              <strong>Ручной режим с веб-интерфейсом:</strong>
            </p>
            <p className="text-sm text-text-secondary mb-3">
              Запустите обучение прямо из браузера с полным отчётом о прогрессе!
            </p>
            <button
              onClick={startTraining}
              disabled={loading || manualExamples.length < 5}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  <span>Обучение запущено...</span>
                </>
              ) : (
                <>
                  <Brain size={20} />
                  <span>🚀 Начать обучение модели</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Отчёт о процессе обучения */}
        {trainingStatus && trainingStatus.log.length > 0 && (
          <div className="p-4 bg-primary-secondary rounded border border-border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2">
                <Zap className="text-accent-cyan" size={18} />
                Процесс обучения
              </h3>
              {trainingStatus.model_name && (
                <span className="text-sm text-accent-cyan font-mono">
                  {trainingStatus.model_name}
                </span>
              )}
            </div>

            {/* Прогресс бар */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-text-secondary">{trainingStatus.stage}</span>
                <span className="text-accent-cyan font-semibold">{trainingStatus.progress}%</span>
              </div>
              <div className="relative h-3 bg-primary-tertiary rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    trainingStatus.error ? 'bg-red-500' :
                    trainingStatus.progress === 100 ? 'bg-green-500' :
                    'bg-accent-cyan'
                  }`}
                  style={{ width: `${trainingStatus.progress}%` }}
                />
              </div>
            </div>

            {/* Лог событий */}
            <div className="space-y-1 max-h-[300px] overflow-y-auto bg-primary-tertiary rounded p-3">
              {trainingStatus.log.map((logEntry, index) => (
                <div key={index} className="text-xs font-mono text-text-secondary">
                  {logEntry}
                </div>
              ))}
            </div>

            {trainingStatus.error && (
              <div className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded">
                <p className="text-sm text-red-400">
                  <strong>Ошибка:</strong> {trainingStatus.error}
                </p>
              </div>
            )}

            {trainingStatus.progress === 100 && !trainingStatus.error && (
              <div className="mt-3 p-3 bg-green-500/10 border border-green-500/30 rounded">
                <p className="text-sm text-green-400">
                  ✅ Обучение успешно завершено! Новая модель доступна в разделе "Сокращалка".
                </p>
              </div>
            )}
          </div>
        )}


        <div className="p-4 bg-primary-secondary rounded">
          <p className="text-xs text-text-secondary space-y-1">
            <strong className="text-text-primary">Рекомендации:</strong><br/>
            • Добавьте минимум 10-20 примеров разной сложности<br/>
            • Используйте разные проценты сокращения (30%, 50%, 70%)<br/>
            • Включайте технические термины, команды, цифры<br/>
            • Чем больше примеров, тем лучше качество модели<br/>
            • Обучение занимает 5-10 минут на каждые 20 примеров
          </p>
        </div>
      </div>
    </div>
  )
}

export default Training
