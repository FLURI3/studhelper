import { useState, useEffect } from 'react'
import { FileText, Trash2, Download, Calendar, Tag, AlertCircle, Loader2 } from 'lucide-react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Documents = () => {
  const { token, isAuthenticated } = useAuth()
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedDoc, setSelectedDoc] = useState(null)

  useEffect(() => {
    if (isAuthenticated) {
      fetchDocuments()
    }
  }, [isAuthenticated])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/my`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
      setDocuments(response.data.documents)
      setError('')
    } catch (err) {
      console.error('Error fetching documents:', err)
      setError('Ошибка загрузки документов')
    } finally {
      setLoading(false)
    }
  }

  const deleteDocument = async (docId) => {
    if (!confirm('Удалить этот документ?')) return

    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${docId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      )
      setDocuments(documents.filter(doc => doc.id !== docId))
      if (selectedDoc?.id === docId) setSelectedDoc(null)
    } catch (err) {
      console.error('Error deleting document:', err)
      alert('Ошибка при удалении документа')
    }
  }

  const downloadDocument = (doc) => {
    const blob = new Blob([doc.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${doc.title || 'document'}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const formatDate = (isoDate) => {
    const date = new Date(isoDate)
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getFileTypeLabel = (type) => {
    const types = {
      'parsed': '📄 Извлечён',
      'shortened': '✂️ Сокращён',
      'analyzed': '📊 Анализ',
      'questions': '❓ Вопросы'
    }
    return types[type] || '📝 Документ'
  }

  if (!isAuthenticated) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Мои документы</h1>
          <p className="text-text-secondary">
            Облачное хранилище обработанных документов
          </p>
        </div>
        <div className="glass-card p-12 text-center">
          <AlertCircle size={48} className="mx-auto mb-4 text-yellow-500" />
          <p className="text-text-secondary">
            Войдите в систему, чтобы сохранять и просматривать документы
          </p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Мои документы</h1>
          <p className="text-text-secondary">
            Облачное хранилище обработанных документов
          </p>
        </div>
        <div className="glass-card p-12 flex flex-col items-center gap-4">
          <Loader2 size={48} className="animate-spin text-accent-cyan" />
          <p className="text-text-secondary">Загружаем документы...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Мои документы</h1>
        <p className="text-text-secondary">
          Облачное хранилище обработанных документов ({documents.length})
        </p>
      </div>

      {error && (
        <div className="glass-card p-4 bg-red-500/10 border border-red-500/30">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {documents.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FileText size={48} className="mx-auto mb-4 text-text-secondary opacity-50" />
          <p className="text-text-secondary mb-2">
            У вас пока нет сохранённых документов
          </p>
          <p className="text-sm text-text-secondary opacity-70">
            Обработайте файлы в Парсере, Сокращателе или Анализаторе и сохраните результаты
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Список документов */}
          <div className="space-y-3">
            {documents.map(doc => (
              <div
                key={doc.id}
                className={`glass-card p-4 cursor-pointer transition-all hover:border-accent-cyan/50 ${
                  selectedDoc?.id === doc.id ? 'border-accent-cyan' : ''
                }`}
                onClick={() => setSelectedDoc(doc)}
              >
                <div className="flex items-start gap-3">
                  <FileText className="text-accent-cyan shrink-0 mt-1" size={20} />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-text-primary truncate mb-1">
                      {doc.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-2 text-xs text-text-secondary">
                      <span className="flex items-center gap-1">
                        <Calendar size={12} />
                        {formatDate(doc.created_at)}
                      </span>
                      {doc.file_type && (
                        <span className="flex items-center gap-1">
                          <Tag size={12} />
                          {getFileTypeLabel(doc.file_type)}
                        </span>
                      )}
                      {doc.original_filename && (
                        <span className="truncate opacity-70">
                          {doc.original_filename}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteDocument(doc.id)
                    }}
                    className="text-red-400 hover:text-red-300 transition-colors shrink-0"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Просмотр документа */}
          <div className="glass-card p-6 sticky top-6 max-h-[calc(100vh-8rem)] flex flex-col">
            {selectedDoc ? (
              <>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h2 className="text-xl font-semibold mb-2">{selectedDoc.title}</h2>
                    <div className="flex flex-wrap gap-2 text-sm text-text-secondary">
                      <span>{formatDate(selectedDoc.created_at)}</span>
                      {selectedDoc.file_type && (
                        <span className="px-2 py-0.5 rounded bg-accent-cyan/20 text-accent-cyan">
                          {getFileTypeLabel(selectedDoc.file_type)}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => downloadDocument(selectedDoc)}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <Download size={16} />
                    Скачать
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto">
                  <div className="whitespace-pre-wrap text-sm text-text-secondary font-mono p-4 bg-bg-secondary/50 rounded-lg">
                    {selectedDoc.content}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <FileText size={48} className="mx-auto mb-4 text-text-secondary opacity-30" />
                  <p className="text-text-secondary">
                    Выберите документ для просмотра
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Documents
