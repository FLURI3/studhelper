import { useState, useEffect } from 'react'
import { HelpCircle, Loader2, Copy, Download } from 'lucide-react'
import axios from 'axios'

const QuestionGenerator = () => {
  const [text, setText] = useState('')
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [count, setCount] = useState(5)
  const [model, setModel] = useState('llama3.2:1b')

  useEffect(() => {
    const savedText = localStorage.getItem('textForQuestions')
    if (savedText) {
      setText(savedText)
      localStorage.removeItem('textForQuestions')
    }
  }, [])

  const handleGenerate = async () => {
    if (!text.trim()) {
      alert('Введите текст для генерации вопросов')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/llm/questions`,
        {
          text: text,
          count: count,
          model: model
        }
      )
      setQuestions(response.data.questions)
    } catch (error) {
      console.error('Error generating questions:', error)
      alert('Ошибка при генерации вопросов')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = () => {
    const allQuestions = questions.join('\n\n')
    navigator.clipboard.writeText(allQuestions)
    alert('Вопросы скопированы')
  }

  const downloadQuestions = () => {
    const blob = new Blob([questions.join('\n\n')], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'questions.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Генератор вопросов</h1>
        <p className="text-text-secondary">
          Автоматическое создание тестовых вопросов из текста с помощью ИИ
        </p>
      </div>

      {/* Settings */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold">Настройки</h2>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Количество вопросов
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={count}
              onChange={(e) => setCount(Math.max(1, Math.min(20, Number(e.target.value))))}
              className="input-field"
            />
          </div>
          
          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Модель
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="input-field"
            >
              <option value="llama3.2:1b">⚡ LLaMA 3.2 1B</option>
              <option value="phi3:mini">⚡ Phi-3 Mini</option>
              <option value="mistral">Mistral 7B</option>
            </select>
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold">Текст для анализа</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="input-field min-h-[200px] font-mono text-sm"
          placeholder="Вставьте текст для генерации вопросов..."
        />
        <button
          onClick={handleGenerate}
          disabled={loading || !text.trim()}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              <span>Генерация...</span>
            </>
          ) : (
            <>
              <HelpCircle size={20} />
              <span>Сгенерировать вопросы</span>
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {questions.length > 0 && (
        <div className="glass-card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Сгенерированные вопросы ({questions.length})</h2>
            <div className="flex gap-2">
              <button
                onClick={copyToClipboard}
                className="btn-secondary flex items-center gap-2"
              >
                <Copy size={20} />
                <span>Копировать</span>
              </button>
              <button
                onClick={downloadQuestions}
                className="btn-secondary flex items-center gap-2"
              >
                <Download size={20} />
                <span>Скачать</span>
              </button>
            </div>
          </div>
          
          <div className="space-y-6">
            {questions.map((question, index) => (
              <div key={index} className="p-4 bg-primary-tertiary rounded-lg">
                <div className="flex items-start gap-3">
                  <span className="text-accent-cyan font-bold">#{index + 1}</span>
                  <p className="flex-1 whitespace-pre-wrap">{question}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default QuestionGenerator
