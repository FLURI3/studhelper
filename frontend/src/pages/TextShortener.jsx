import { useState, useEffect } from 'react'
import { Scissors, Loader2, Copy, Download, CheckCircle, AlertCircle, Info, RefreshCw } from 'lucide-react'
import axios from 'axios'

const MAX_TEXT_LENGTH = 100000

const TextShortener = () => {
  const [inputText, setInputText] = useState('')
  const [shortenedText, setShortenedText] = useState('')
  const [loading, setLoading] = useState(false)
  const [ratio, setRatio] = useState(50)
  const [model, setModel] = useState('mistral')
  const [customPrompt, setCustomPrompt] = useState('')
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState('')
  const [reasoning, setReasoning] = useState('')
  const [trainingStats, setTrainingStats] = useState(null)
  const [trainedModels, setTrainedModels] = useState([])

  // Загружаем текст из localStorage и статистику обучения при монтировании
  useEffect(() => {
    const savedText = localStorage.getItem('textToShorten')
    if (savedText) {
      setInputText(savedText)
      localStorage.removeItem('textToShorten')
    }
    
    fetchTrainingStats()
    // Обновляем статистику каждые 30 секунд
    const interval = setInterval(fetchTrainingStats, 30000)
    return () => clearInterval(interval)
  }, [])
  
  const fetchTrainingStats = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/training/stats`
      )
      setTrainingStats(response.data)
      setTrainedModels(response.data.trained_models || [])
      
      // Автоматически выбираем последнюю обученную модель, если она есть
      if (response.data.latest_model && !model.includes('summarizer')) {
        setModel(response.data.latest_model)
      }
    } catch (error) {
      console.error('Error fetching training stats:', error)
    }
  }

  const isTextTooLong = inputText.length > MAX_TEXT_LENGTH
  const textLengthPercent = Math.min((inputText.length / MAX_TEXT_LENGTH) * 100, 100)
  const getLengthColor = () => {
    if (textLengthPercent < 50) return 'text-green-500'
    if (textLengthPercent < 80) return 'text-yellow-500'
    return 'text-red-500'
  }

  const handleShorten = async () => {
    if (!inputText.trim()) {
      alert('Введите текст для сокращения')
      return
    }

    setLoading(true)
    setError(null)
    setProgress('Подключение к Ollama...')
    
    try {
      setProgress('Отправка текста на обработку...')
      
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/llm/summarize`,
        {
          text: inputText,
          ratio: ratio,
          model: model,
          custom_prompt: customPrompt
        }
      )
      
      setProgress('Получение результата...')
      setShortenedText(response.data.summary)
      setReasoning(response.data.reasoning || '')
      setStats({
        original: response.data.original_length,
        summary: response.data.summary_length,
        ratio: response.data.compression_ratio
      })
      setProgress('Готово!')
      
    } catch (error) {
      console.error('Error shortening text:', error)
      const errorMsg = error.response?.data?.detail || error.message || 'Ошибка при сокращении текста'
      setError(errorMsg)
      setProgress('')
    } finally {
      setLoading(false)
      setTimeout(() => setProgress(''), 2000)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Текст скопирован')
  }

  const downloadText = (text, filename) => {
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Умное сокращение текста</h1>
        <p className="text-text-secondary">
          Используйте ИИ для создания краткого резюме вашего текста
        </p>
      </div>

      {/* Settings */}
      <div className="glass-card p-6 space-y-6">
        <h2 className="text-xl font-semibold">Настройки</h2>
        
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm text-text-secondary">
              Модель Ollama (⚡ = быстрая)
            </label>
            {trainingStats && (
              <button
                onClick={fetchTrainingStats}
                className="text-xs text-accent-cyan hover:text-accent-cyan/80 flex items-center gap-1"
              >
                <RefreshCw size={12} />
                Обновить
              </button>
            )}
          </div>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="input-field"
          >
            <optgroup label="🎯 Обученные модели">
              {trainedModels.map(m => (
                <option key={m} value={m}>
                  {m} {m === trainingStats?.latest_model ? '⭐ Новейшая' : ''}
                </option>
              ))}
            </optgroup>
            <optgroup label="📦 Базовые модели">
              <option value="mistral">🌟 Mistral 7B (Рекомендуется)</option>
              <option value="llama2">LLaMA 2 7B</option>
              <option value="phi3:mini">⚡ Phi-3 Mini</option>
              <option value="llama3.2:1b">⚡ LLaMA 3.2 1B</option>
            </optgroup>
          </select>
          {trainingStats && (
            <div className="mt-2 p-2 bg-primary-tertiary rounded text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">Прогресс обучения:</span>
                <span className="font-semibold text-accent-cyan">
                  {trainingStats.current_progress} / {trainingStats.auto_train_threshold}
                </span>
              </div>
              <div className="relative h-1.5 bg-primary-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent-cyan transition-all duration-300"
                  style={{ width: `${trainingStats.progress_percentage}%` }}
                />
              </div>
              <p className="text-text-secondary text-[10px]">
                {trainingStats.auto_train_enabled ? (
                  <>
                    🤖 Автообучение: ещё {trainingStats.next_training_in} примеров до новой версии
                  </>
                ) : (
                  <>📊 Собрано {trainingStats.total_examples} примеров (автообучение выключено)</>
                )}
              </p>
            </div>
          )}
        </div>

        <div>
          <div className="flex justify-between items-center mb-3">
            <label className="text-sm text-text-secondary">
              Степень сокращения
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="10"
                max="80"
                value={ratio}
                onChange={(e) => setRatio(Math.min(80, Math.max(10, Number(e.target.value))))}
                className="w-16 px-2 py-1 bg-primary-tertiary border border-border rounded text-center"
              />
              <span className="text-sm">%</span>
            </div>
          </div>
          <input
            type="range"
            min="10"
            max="80"
            value={ratio}
            onChange={(e) => setRatio(Number(e.target.value))}
            className="w-full h-2 bg-primary-tertiary rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #00d9ff 0%, #00d9ff ${(ratio - 10) / 0.7}%, #2d2d2d ${(ratio - 10) / 0.7}%, #2d2d2d 100%)`
            }}
          />
          <div className="flex justify-between text-xs text-text-secondary mt-2">
            <span>📝 Очень кратко</span>
            <span>📄 Подробно</span>
          </div>
        </div>

        <div>
          <label className="block text-sm text-text-secondary mb-2">
            Дополнительные инструкции (опционально)
          </label>
          <textarea
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            className="input-field min-h-[80px] text-sm"
            placeholder="Например: 'Сделай акцент на технических деталях' или 'Убери все примеры'"
          />
        </div>
      </div>

      {/* Progress / Error */}
      {loading && (
        <div className="glass-card p-4 flex items-center gap-3 border-l-4 border-accent-cyan">
          <Loader2 size={20} className="animate-spin text-accent-cyan" />
          <div className="flex-1">
            <p className="font-medium">Обработка текста...</p>
            <p className="text-sm text-text-secondary">{progress}</p>
          </div>
        </div>
      )}

      {error && (
        <div className="glass-card p-4 flex items-center gap-3 border-l-4 border-red-500">
          <AlertCircle size={20} className="text-red-500" />
          <div className="flex-1">
            <p className="font-medium text-red-500">Ошибка</p>
            <p className="text-sm text-text-secondary">{error}</p>
          </div>
        </div>
      )}

      {stats && !loading && (
        <div className="glass-card p-4 border-l-4 border-green-500 space-y-3">
          <div className="flex items-center gap-3">
            <CheckCircle size={20} className="text-green-500" />
            <div className="flex-1">
              <p className="font-medium text-green-500">Успешно обработано</p>
              <p className="text-sm text-text-secondary">
                {stats.original} символов → {stats.summary} символов (фактическое сжатие {stats.ratio}%)
              </p>
            </div>
          </div>
          
          {reasoning && (
            <div className="pl-8 pt-2 border-t border-border">
              <p className="text-xs text-text-secondary mb-1 font-semibold">🤔 Рассуждение ИИ:</p>
              <p className="text-sm text-text-secondary italic">{reasoning}</p>
            </div>
          )}
        </div>
      )}

      {/* Input and Output */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Исходный текст</h2>
            <div className="flex items-center gap-2">
              <span className={`text-sm font-semibold ${getLengthColor()}`}>
                {inputText.length.toLocaleString()} / {MAX_TEXT_LENGTH.toLocaleString()}
              </span>
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="relative h-2 bg-primary-tertiary rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${
                isTextTooLong ? 'bg-red-500' : textLengthPercent < 50 ? 'bg-green-500' : textLengthPercent < 80 ? 'bg-yellow-500' : 'bg-orange-500'
              }`}
              style={{ width: `${textLengthPercent}%` }}
            />
          </div>
          
          {isTextTooLong && (
            <div className="flex items-center gap-2 text-red-500 text-sm">
              <AlertCircle size={16} />
              <span>Текст слишком большой! Максимум {MAX_TEXT_LENGTH.toLocaleString()} символов</span>
            </div>
          )}
          
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className={`input-field min-h-[400px] font-mono text-sm ${
              isTextTooLong ? 'border-red-500 focus:border-red-500' : ''
            }`}
            placeholder="Вставьте или введите текст для сокращения..."
            maxLength={MAX_TEXT_LENGTH}
          />
          <button
            onClick={handleShorten}
            disabled={loading || !inputText.trim() || isTextTooLong}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                <span>Обработка...</span>
              </>
            ) : (
              <>
                <Scissors size={20} />
                <span>Сократить текст</span>
              </>
            )}
          </button>
        </div>

        {/* Output */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Сокращённый текст</h2>
            {shortenedText && (
              <span className="text-sm text-text-secondary">
                {shortenedText.length} символов
              </span>
            )}
          </div>
          <textarea
            value={shortenedText}
            readOnly
            className="input-field min-h-[400px] font-mono text-sm"
            placeholder="Результат появится здесь..."
          />
          {shortenedText && (
            <div className="flex gap-3">
              <button
                onClick={() => copyToClipboard(shortenedText)}
                className="btn-secondary flex-1 flex items-center justify-center gap-2"
              >
                <Copy size={20} />
                <span>Копировать</span>
              </button>
              <button
                onClick={() => downloadText(shortenedText, 'shortened.txt')}
                className="btn-secondary flex-1 flex items-center justify-center gap-2"
              >
                <Download size={20} />
                <span>Скачать</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TextShortener
