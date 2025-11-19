import { useState, useRef } from 'react'
import { Upload, X, FileText } from 'lucide-react'

const FileUpload = ({ onFileSelect, accept = "*", maxSize = 10485760 }) => {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const inputRef = useRef(null)

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

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    if (file.size > maxSize) {
      alert(`Файл слишком большой. Максимум ${maxSize / 1024 / 1024} MB`)
      return
    }
    setSelectedFile(file)
    onFileSelect(file)
  }

  const clearFile = () => {
    setSelectedFile(null)
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <div
        className={`glass-card p-12 text-center border-2 border-dashed transition-all cursor-pointer ${
          dragActive ? 'border-accent-cyan bg-accent-cyan/5' : 'border-border'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={accept}
          onChange={handleChange}
        />
        
        <Upload size={48} className="mx-auto mb-4 text-accent-cyan" />
        <p className="text-xl mb-2">
          Перетащите файл сюда или нажмите для выбора
        </p>
        <p className="text-sm text-text-secondary">
          Максимальный размер: {maxSize / 1024 / 1024} MB
        </p>
      </div>

      {selectedFile && (
        <div className="glass-card p-4 flex items-center gap-3">
          <FileText className="text-accent-cyan" />
          <div className="flex-1">
            <p className="font-medium">{selectedFile.name}</p>
            <p className="text-sm text-text-secondary">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation()
              clearFile()
            }}
            className="p-2 hover:bg-primary-tertiary rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>
      )}
    </div>
  )
}

export default FileUpload
