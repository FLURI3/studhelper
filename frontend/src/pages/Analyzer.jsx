import { useState, useEffect } from 'react'
import { BarChart3, Loader2 } from 'lucide-react'
import axios from 'axios'

const Analyzer = () => {
  const [text, setText] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)

  // Загружаем текст из localStorage при монтировании
  useEffect(() => {
    const savedText = localStorage.getItem('textToAnalyze')
    if (savedText) {
      setText(savedText)
      localStorage.removeItem('textToAnalyze') // Очищаем после загрузки
    }
  }, [])

  const handleAnalyze = async () => {
    if (!text.trim()) {
      alert('Введите текст для анализа')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/analyzer/stats`,
        { text }
      )
      setAnalysis(response.data)
    } catch (error) {
      console.error('Error analyzing text:', error)
      alert('Ошибка при анализе текста')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Анализ текста</h1>
        <p className="text-text-secondary">
          Получите детальную статистику и ключевые термины из текста
        </p>
      </div>

      {/* Input */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold">Текст для анализа</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="input-field min-h-[300px] font-mono text-sm"
          placeholder="Вставьте текст для анализа..."
        />
        <button
          onClick={handleAnalyze}
          disabled={loading || !text.trim()}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              <span>Анализируем...</span>
            </>
          ) : (
            <>
              <BarChart3 size={20} />
              <span>Анализировать</span>
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-card p-6 text-center">
              <div className="text-3xl font-bold text-accent-cyan mb-2">
                {analysis.word_count}
              </div>
              <div className="text-text-secondary">Слов</div>
            </div>
            <div className="glass-card p-6 text-center">
              <div className="text-3xl font-bold text-accent-purple mb-2">
                {analysis.sentence_count}
              </div>
              <div className="text-text-secondary">Предложений</div>
            </div>
            <div className="glass-card p-6 text-center">
              <div className="text-3xl font-bold text-accent-cyan mb-2">
                {analysis.char_count}
              </div>
              <div className="text-text-secondary">Символов</div>
            </div>
            <div className="glass-card p-6 text-center">
              <div className="text-3xl font-bold text-accent-purple mb-2">
                {analysis.read_time}
              </div>
              <div className="text-text-secondary">Мин. читать</div>
            </div>
          </div>

          {/* Key Terms */}
          {analysis.key_terms && (
            <div className="glass-card p-6 space-y-4">
              <h2 className="text-xl font-semibold">Ключевые термины</h2>
              <div className="flex flex-wrap gap-2">
                {analysis.key_terms.map((term, index) => (
                  <span
                    key={index}
                    className="px-4 py-2 bg-accent-cyan/20 text-accent-cyan rounded-full text-sm"
                  >
                    {term}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Readability */}
          <div className="glass-card p-6 space-y-4">
            <h2 className="text-xl font-semibold">Читаемость</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-text-secondary">Сложность текста</span>
                <span className="font-semibold">{analysis.complexity || 'Средняя'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Среднее слов в предложении</span>
                <span className="font-semibold">
                  {(analysis.word_count / analysis.sentence_count).toFixed(1)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Analyzer
