import { useState } from 'react'
import { Upload, FileText, Loader2, Scissors, BarChart3, HelpCircle, Save, Check } from 'lucide-react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Parser = () => {
  const navigate = useNavigate()
  const { token, isAuthenticated } = useAuth()
  const [file, setFile] = useState(null)
  const [extractedText, setExtractedText] = useState('')
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (selectedFile) => {
    setFile(selectedFile)
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/parser/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )

      setExtractedText(response.data.text)
    } catch (error) {
      console.error('Error parsing file:', error)
      alert('Ошибка при парсинге файла')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(extractedText)
    alert('Текст скопирован в буфер обмена')
  }

  const handleShortenText = () => {
    // Сохраняем текст в localStorage и переходим на страницу сокращения
    localStorage.setItem('textToShorten', extractedText)
    navigate('/shortener')
  }

  const handleAnalyzeText = () => {
    // Сохраняем текст в localStorage и переходим на страницу анализа
    localStorage.setItem('textToAnalyze', extractedText)
    navigate('/analyzer')
  }

  const saveToCloud = async () => {
    if (!isAuthenticated) {
      alert('Войдите в систему, чтобы сохранять документы')
      navigate('/login')
      return
    }

    setSaving(true)
    try {
      await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/save`,
        {
          title: file?.name || 'Извлечённый текст',
          content: extractedText,
          original_filename: file?.name,
          file_type: 'parsed',
          metadata: {
            file_size: file?.size,
            extracted_at: new Date().toISOString()
          }
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('Error saving document:', error)
      alert('Ошибка при сохранении документа')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Парсер документов</h1>
        <p className="text-text-secondary">
          Загрузите PDF, PPTX, DOCX или изображение для извлечения текста
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`glass-card p-12 text-center border-2 border-dashed transition-all ${
          dragActive ? 'border-accent-cyan bg-accent-cyan/5' : 'border-border'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".pdf,.pptx,.docx,.doc,.txt,.jpg,.jpeg,.png,.gif,.bmp,.tiff"
          onChange={handleFileInput}
        />
        
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload size={48} className="mx-auto mb-4 text-accent-cyan" />
          <p className="text-xl mb-2">
            Перетащите файл сюда или нажмите для выбора
          </p>
          <p className="text-sm text-text-secondary">
            Поддерживаются: PDF, PPTX, DOCX, TXT, JPG, PNG, GIF, BMP, TIFF
          </p>
          <p className="text-xs text-text-secondary mt-2 opacity-70">
            📄 Документы | 🖼️ Изображения (с OCR) | 📊 Презентации
          </p>
        </label>
      </div>

      {/* File Info */}
      {file && (
        <div className="glass-card p-4 flex items-center gap-3">
          <FileText className="text-accent-cyan" />
          <span className="flex-1">{file.name}</span>
          <span className="text-text-secondary text-sm">
            {(file.size / 1024).toFixed(2)} KB
          </span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="glass-card p-12 flex flex-col items-center gap-4">
          <Loader2 size={48} className="animate-spin text-accent-cyan" />
          <p className="text-text-secondary">Извлекаем текст из документа...</p>
        </div>
      )}

      {/* Extracted Text */}
      {extractedText && !loading && (
        <div className="glass-card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Извлечённый текст</h2>
            <button onClick={copyToClipboard} className="btn-secondary">
              Копировать
            </button>
          </div>
          <textarea
            value={extractedText}
            onChange={(e) => setExtractedText(e.target.value)}
            className="input-field min-h-[400px] font-mono text-sm"
            placeholder="Извлечённый текст появится здесь..."
          />
          <div className="space-y-3">
            <button
              onClick={saveToCloud}
              disabled={saving || saved}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-70"
            >
              {saved ? (
                <>
                  <Check size={20} />
                  <span>Сохранено в облако!</span>
                </>
              ) : saving ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  <span>Сохранение...</span>
                </>
              ) : (
                <>
                  <Save size={20} />
                  <span>💾 Сохранить в облако</span>
                </>
              )}
            </button>
            <div className="grid grid-cols-3 gap-3">
              <button 
                onClick={handleShortenText}
                className="btn-secondary flex items-center justify-center gap-2"
              >
                <Scissors size={20} />
                <span>Сократить</span>
              </button>
              <button 
                onClick={handleAnalyzeText}
                className="btn-secondary flex items-center justify-center gap-2"
              >
                <BarChart3 size={20} />
                <span>Анализ</span>
              </button>
              <button 
                onClick={() => {
                  localStorage.setItem('textForQuestions', extractedText)
                  navigate('/questions')
                }}
                className="btn-secondary flex items-center justify-center gap-2"
              >
                <HelpCircle size={20} />
                <span>Вопросы</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Parser
