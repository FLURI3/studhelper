import { Link, useLocation } from 'react-router-dom'
import { BookOpen, FileText, Scissors, BarChart3, HelpCircle, FolderOpen, Brain, Wrench, GraduationCap, ChevronDown, Calendar, Menu, X, LogIn, UserPlus, LogOut, User } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'

const Layout = ({ children }) => {
  const location = useLocation()
  const { user, logout, isAuthenticated } = useAuth()
  const [openCategory, setOpenCategory] = useState('tools')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navCategories = {
    main: [
      { path: '/', icon: BookOpen, label: 'Главная' }
    ],
    tools: [
      { path: '/shortener', icon: Scissors, label: 'Сокращалка' },
      { path: '/parser', icon: FileText, label: 'Парсер' },
      { path: '/analyzer', icon: BarChart3, label: 'Анализатор' },
      { path: '/questions', icon: HelpCircle, label: 'Генератор вопросов' },
      { path: '/training', icon: Brain, label: 'Обучение модели' },
    ],
    student: [
      { path: '/schedule', icon: Calendar, label: 'Расписание' },
      { path: '/documents', icon: FolderOpen, label: 'Документы' },
    ]
  }

  const toggleCategory = (category) => {
    setOpenCategory(openCategory === category ? null : category)
  }

  const closeSidebar = () => setSidebarOpen(false)

  return (
    <div className="min-h-screen flex">
      {/* Mobile menu button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-primary-secondary/95 backdrop-blur-sm border border-border hover:bg-primary-tertiary transition-colors"
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside className={`w-64 bg-primary-secondary border-r border-border fixed h-full overflow-y-auto z-40 transition-transform duration-300 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0`}>
        <div className="p-6">
          <h1 className="text-2xl font-bold text-accent-cyan mb-8">
            Student Helper
          </h1>
          <nav className="space-y-1">
            {/* Главная */}
            {navCategories.main.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={closeSidebar}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30'
                      : 'text-text-secondary hover:bg-primary-tertiary hover:text-text-primary'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}

            {/* Инструменты */}
            <div className="mt-6">
              <button
                onClick={() => toggleCategory('tools')}
                className="flex items-center justify-between w-full px-4 py-2 text-sm font-semibold text-text-secondary hover:text-text-primary transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Wrench size={18} />
                  <span>Инструменты</span>
                </div>
                <ChevronDown
                  size={16}
                  className={`transition-transform ${openCategory === 'tools' ? 'rotate-180' : ''}`}
                />
              </button>
              {openCategory === 'tools' && (
                <div className="mt-1 space-y-1 pl-2">
                  {navCategories.tools.map((item) => {
                    const Icon = item.icon
                    const isActive = location.pathname === item.path
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        onClick={closeSidebar}
                        className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-200 text-sm ${
                          isActive
                            ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30'
                            : 'text-text-secondary hover:bg-primary-tertiary hover:text-text-primary'
                        }`}
                      >
                        <Icon size={18} />
                        <span>{item.label}</span>
                      </Link>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Для учёбы */}
            <div className="mt-4">
              <button
                onClick={() => toggleCategory('student')}
                className="flex items-center justify-between w-full px-4 py-2 text-sm font-semibold text-text-secondary hover:text-text-primary transition-colors"
              >
                <div className="flex items-center gap-2">
                  <GraduationCap size={18} />
                  <span>Для учёбы</span>
                </div>
                <ChevronDown
                  size={16}
                  className={`transition-transform ${openCategory === 'student' ? 'rotate-180' : ''}`}
                />
              </button>
              {openCategory === 'student' && (
                <div className="mt-1 space-y-1 pl-2">
                  {navCategories.student.map((item) => {
                    const Icon = item.icon
                    const isActive = location.pathname === item.path
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        onClick={closeSidebar}
                        className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-200 text-sm ${
                          isActive
                            ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30'
                            : 'text-text-secondary hover:bg-primary-tertiary hover:text-text-primary'
                        }`}
                      >
                        <Icon size={18} />
                        <span>{item.label}</span>
                      </Link>
                    )
                  })}
                </div>
              )}
            </div>
          </nav>

          {/* Auth Section */}
          <div className="mt-8 pt-6 border-t border-border">
            {isAuthenticated ? (
              <div className="space-y-2">
                <Link
                  to="/profile"
                  onClick={closeSidebar}
                  className={`flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-all duration-200 ${
                    location.pathname === '/profile'
                      ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30'
                      : 'text-text-secondary hover:bg-primary-tertiary hover:text-text-primary'
                  }`}
                >
                  <User size={18} />
                  <div className="flex-1">
                    <div className="font-medium">{user?.username}</div>
                    {user?.group && (
                      <div className="text-xs opacity-70">{user.group}</div>
                    )}
                  </div>
                </Link>
                <button
                  onClick={() => {
                    logout()
                    closeSidebar()
                  }}
                  className="flex items-center gap-3 px-4 py-2 rounded-lg text-sm text-text-secondary hover:bg-red-500/20 hover:text-red-400 transition-all duration-200 w-full"
                >
                  <LogOut size={18} />
                  <span>Выйти</span>
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Link
                  to="/login"
                  onClick={closeSidebar}
                  className="flex items-center gap-3 px-4 py-2 rounded-lg text-sm text-text-secondary hover:bg-primary-tertiary hover:text-text-primary transition-all duration-200"
                >
                  <LogIn size={18} />
                  <span>Войти</span>
                </Link>
                <Link
                  to="/register"
                  onClick={closeSidebar}
                  className="flex items-center gap-3 px-4 py-2 rounded-lg text-sm bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30 hover:bg-accent-cyan/30 transition-all duration-200"
                >
                  <UserPlus size={18} />
                  <span>Регистрация</span>
                </Link>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-0 md:ml-64 flex-1 p-4 md:p-8 pt-16 md:pt-8">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
