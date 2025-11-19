import { Link } from 'react-router-dom'
import { FileText, Scissors, BarChart3, HelpCircle, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

const Home = () => {
  const features = [
    {
      icon: FileText,
      title: 'Парсер документов',
      description: 'Извлекайте текст из PDF, PPTX, DOCX и изображений',
      link: '/parser',
      color: 'cyan',
    },
    {
      icon: Scissors,
      title: 'Умное сокращение',
      description: 'Сокращайте тексты с помощью ИИ до нужного объёма',
      link: '/shortener',
      color: 'purple',
    },
    {
      icon: BarChart3,
      title: 'Анализ текста',
      description: 'Получите статистику и ключевые термины из документа',
      link: '/analyzer',
      color: 'cyan',
    },
    {
      icon: HelpCircle,
      title: 'Генератор вопросов',
      description: 'Создавайте тестовые вопросы автоматически',
      link: '/questions',
      color: 'purple',
    },
  ]

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-6 py-12"
      >
        <h1 className="text-5xl font-bold">
          <span className="text-accent-cyan">Student</span> Helper
        </h1>
        <p className="text-xl text-text-secondary max-w-2xl mx-auto">
          Современный инструмент для помощи в обучении. Парсинг документов, умное сокращение текстов и многое другое.
        </p>
      </motion.div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature, index) => {
          const Icon = feature.icon
          return (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Link to={feature.link}>
                <div className="glass-card p-8 hover:scale-[1.02] transition-transform duration-200 group">
                  <div className={`inline-flex p-3 rounded-lg mb-4 ${
                    feature.color === 'cyan' 
                      ? 'bg-accent-cyan/20 text-accent-cyan' 
                      : 'bg-accent-purple/20 text-accent-purple'
                  }`}>
                    <Icon size={32} />
                  </div>
                  <h3 className="text-2xl font-semibold mb-3">{feature.title}</h3>
                  <p className="text-text-secondary mb-4">{feature.description}</p>
                  <div className="flex items-center text-accent-cyan group-hover:gap-2 transition-all">
                    <span>Начать</span>
                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            </motion.div>
          )
        })}
      </div>

      {/* Stats Section */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="glass-card p-8"
      >
        <h2 className="text-2xl font-semibold mb-6 text-center">Возможности</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="space-y-2">
            <div className="text-4xl font-bold text-accent-cyan mb-2">8+</div>
            <div className="text-text-secondary text-sm">Форматов документов</div>
            <div className="text-xs text-text-secondary opacity-70">PDF, DOCX, PPTX, JPG, PNG и др.</div>
          </div>
          <div className="space-y-2">
            <div className="text-4xl font-bold text-accent-purple mb-2">⚡ AI</div>
            <div className="text-text-secondary text-sm">Обработка через Ollama</div>
            <div className="text-xs text-text-secondary opacity-70">LLaMA 3.2, Mistral, Phi-3</div>
          </div>
          <div className="space-y-2">
            <div className="text-4xl font-bold text-accent-cyan mb-2">100K</div>
            <div className="text-text-secondary text-sm">Символов за раз</div>
            <div className="text-xs text-text-secondary opacity-70">Обработка больших текстов</div>
          </div>
          <div className="space-y-2">
            <div className="text-4xl font-bold text-accent-purple mb-2">∞</div>
            <div className="text-text-secondary text-sm">Бесплатно</div>
            <div className="text-xs text-text-secondary opacity-70">Без ограничений и подписок</div>
          </div>
        </div>
      </motion.div>

      {/* Additional Features */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold mb-4 text-accent-cyan">🚀 Технологии</h3>
          <ul className="space-y-2 text-text-secondary">
            <li>• React 18 + Vite - быстрый интерфейс</li>
            <li>• FastAPI + Python - мощный backend</li>
            <li>• Ollama - локальные LLM модели</li>
            <li>• Docker - простое развёртывание</li>
            <li>• Tailwind CSS - современный дизайн</li>
          </ul>
        </div>
        
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold mb-4 text-accent-purple">✨ Особенности</h3>
          <ul className="space-y-2 text-text-secondary">
            <li>• Кастомные промпты для сокращения</li>
            <li>• Автоматическая генерация вопросов</li>
            <li>• OCR для извлечения текста из картинок</li>
            <li>• Анализ сложности и статистики текста</li>
            <li>• Экспорт результатов в файлы</li>
          </ul>
        </div>
      </motion.div>
    </div>
  )
}

export default Home
