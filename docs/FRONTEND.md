# 🎨 Frontend Documentation

> Документация по архитектуре, компонентам и разработке React приложения Student Helper

## 📋 Содержание

- [Обзор](#обзор)
- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)
- [Компоненты](#компоненты)
- [Страницы](#страницы)
- [Стилизация](#стилизация)
- [API интеграция](#api-интеграция)
- [Разработка](#разработка)

## 🎯 Обзор

Frontend приложение Student Helper построено на современном стеке:
- **React 18.2** — для построения UI
- **Vite 5.0** — быстрая сборка и HMR
- **Tailwind CSS 3.4** — utility-first стилизация
- **React Router 6** — клиентский роутинг
- **Axios** — HTTP запросы к API

### Ключевые особенности

✅ **Адаптивный дизайн** — работает на десктопах, планшетах и мобильных
✅ **Тёмная тема** — современный минималистичный интерфейс
✅ **Быстрая загрузка** — Vite обеспечивает мгновенный HMR
✅ **Модульная структура** — легко добавлять новые страницы
✅ **Type safety** — JSDoc комментарии для лучшего DX

## 🏗️ Архитектура

### Component Tree

```
App
├── Layout (навигация + sidebar)
│   ├── Burger Menu (mobile)
│   ├── Navigation Links
│   └── Main Content Area
│       └── [Page Component]
│
└── Routes
    ├── Home
    ├── Parser
    ├── TextShortener
    ├── Analyzer
    ├── QuestionGenerator
    ├── Schedule
    ├── Documents
    └── Training
```

### Паттерны и подходы

**Composition over Inheritance**
```jsx
// Переиспользуемые компоненты через composition
<Layout>
  <PageHeader title="Расписание" />
  <PageContent>
    <ScheduleGrid />
  </PageContent>
</Layout>
```

**Container/Presentation Pattern**
```jsx
// Container компонент с логикой
const ScheduleContainer = () => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  
  return <ScheduleView data={data} loading={loading} />
}

// Presentation компонент без логики
const ScheduleView = ({ data, loading }) => (
  <div>{loading ? <Spinner /> : <ScheduleGrid data={data} />}</div>
)
```

**Custom Hooks для переиспользования логики**
```jsx
// hooks/useSchedule.js
const useSchedule = (groupCode) => {
  const [schedule, setSchedule] = useState(null)
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    fetchSchedule(groupCode)
  }, [groupCode])
  
  return { schedule, loading }
}
```

## 📂 Структура проекта

```
frontend/
├── public/
│   └── vite.svg              # Favicon
│
├── src/
│   ├── components/           # Переиспользуемые компоненты
│   │   ├── Layout/
│   │   │   └── Layout.jsx    # Главный макет с навигацией
│   │   ├── FileUpload.jsx    # Загрузка файлов
│   │   └── LoadingSpinner.jsx
│   │
│   ├── pages/                # Страницы приложения
│   │   ├── Home.jsx          # Главная страница
│   │   ├── Parser.jsx        # Парсер документов
│   │   ├── TextShortener.jsx # Сокращение текста
│   │   ├── Analyzer.jsx      # Анализ текста
│   │   ├── QuestionGenerator.jsx
│   │   ├── Schedule.jsx      # Расписание СГТУ
│   │   ├── Documents.jsx     # Управление документами
│   │   └── Training.jsx      # Обучение моделей
│   │
│   ├── App.jsx               # Роутинг приложения
│   ├── main.jsx              # Точка входа
│   └── index.css             # Глобальные стили
│
├── .eslintrc.cjs             # ESLint конфигурация
├── postcss.config.js         # PostCSS для Tailwind
├── tailwind.config.js        # Tailwind настройки
├── vite.config.js            # Vite конфигурация
├── package.json              # Зависимости
├── Dockerfile                # Docker образ
└── index.html                # HTML шаблон
```

## 🧩 Компоненты

### Layout Component

**Файл**: `src/components/Layout/Layout.jsx`

Главный layout с адаптивной боковой навигацией.

**Особенности:**
- Burger menu для мобильных устройств
- Автоматическое закрытие sidebar при навигации
- Категоризация меню (Главная, Инструменты, Для учёбы)
- Подсветка активного раздела

**Props:**
```jsx
{
  children: ReactNode  // Контент страницы
}
```

**Состояние:**
```jsx
const [openCategory, setOpenCategory] = useState('tools')
const [sidebarOpen, setSidebarOpen] = useState(false)
```

**Пример использования:**
```jsx
import Layout from './components/Layout/Layout'

function App() {
  return (
    <Layout>
      <h1>Содержимое страницы</h1>
    </Layout>
  )
}
```

### FileUpload Component

**Файл**: `src/components/FileUpload.jsx`

Drag & Drop загрузка файлов с preview.

**Props:**
```jsx
{
  onFileSelect: (file: File) => void,
  accept: string,              // ".pdf,.docx,.pptx"
  maxSize: number,             // в байтах
  multiple: boolean
}
```

**Пример:**
```jsx
<FileUpload
  onFileSelect={(file) => handleUpload(file)}
  accept=".pdf,.docx,.pptx"
  maxSize={10 * 1024 * 1024}  // 10MB
  multiple={false}
/>
```

### LoadingSpinner Component

**Файл**: `src/components/LoadingSpinner.jsx`

Анимированный индикатор загрузки.

**Props:**
```jsx
{
  size?: 'sm' | 'md' | 'lg',
  text?: string
}
```

**Пример:**
```jsx
{loading && <LoadingSpinner size="lg" text="Загрузка расписания..." />}
```

## 📄 Страницы

### Home Page

**Файл**: `src/pages/Home.jsx`  
**Маршрут**: `/`

Главная страница с описанием функционала и быстрыми ссылками.

**Структура:**
- Hero секция с описанием
- Карточки функций с иконками
- Статистика использования
- CTA кнопки

### Parser Page

**Файл**: `src/pages/Parser.jsx`  
**Маршрут**: `/parser`

Загрузка и парсинг документов (PDF, DOCX, PPTX).

**Функционал:**
- Drag & Drop загрузка
- Валидация формата и размера
- Progress bar загрузки
- Отображение результата парсинга
- Экспорт в Markdown/JSON/TXT

**API взаимодействие:**
```jsx
const handleUpload = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await axios.post(
    `${API_URL}/api/parser/upload`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        setProgress((e.loaded / e.total) * 100)
      }
    }
  )
  
  setResult(response.data)
}
```

### TextShortener Page

**Файл**: `src/pages/TextShortener.jsx`  
**Маршрут**: `/shortener`

Умное сокращение текста через LLM.

**Функционал:**
- Textarea для ввода текста
- Выбор модели (Mistral, Gemma)
- Slider для выбора степени сокращения (10-90%)
- Сравнение оригинала и результата
- Копирование/экспорт результата
- Автоматический сбор обучающих примеров

**Состояние:**
```jsx
const [inputText, setInputText] = useState('')
const [outputText, setOutputText] = useState('')
const [ratio, setRatio] = useState(0.3)
const [model, setModel] = useState('mistral')
const [loading, setLoading] = useState(false)
```

**API запрос:**
```jsx
const handleSummarize = async () => {
  setLoading(true)
  try {
    const response = await axios.post(
      `${API_URL}/api/llm/summarize`,
      {
        text: inputText,
        ratio: ratio,
        model: model
      }
    )
    setOutputText(response.data.summary)
  } catch (error) {
    console.error('Ошибка сокращения:', error)
  } finally {
    setLoading(false)
  }
}
```

### Schedule Page

**Файл**: `src/pages/Schedule.jsx`  
**Маршрут**: `/schedule`

Расписание занятий СГТУ с парсингом официального сайта.

**Функционал:**
- Загрузка списка всех групп
- Поиск по названию группы
- Фильтрация по специальностям (ИСП, МТО, ТОА и т.д.)
- Отображение расписания на все недели
- Выделение текущего дня
- Поддержка подгрупп
- Мобильная адаптация

**Структура данных:**
```jsx
// Группа
{
  code: "74",           // cg74.htm
  name: "ИСП-12"
}

// Расписание
{
  group_code: "74",
  group_name: "ИСП-12",
  schedule_days: [
    {
      day: "Понедельник",
      date: "17.11.2025",
      day_of_week: 0,
      lessons: [
        {
          number: "1",
          time: "08:30-10:00",
          subject: "Математика",
          teacher: "Иванов И.И.",
          room: "201",
          type: "Лекция"
        }
      ]
    }
  ],
  last_updated: "2025-11-19 14:30:00"
}
```

**Ключевые функции:**

```jsx
// Группировка пар по времени (для подгрупп)
const groupLessonsByTime = (lessons) => {
  const grouped = {}
  lessons.forEach(lesson => {
    const key = `${lesson.number}-${lesson.time}`
    if (!grouped[key]) {
      grouped[key] = {
        number: lesson.number,
        time: lesson.time,
        variants: []
      }
    }
    grouped[key].variants.push({
      subject: lesson.subject,
      teacher: lesson.teacher,
      room: lesson.room,
      type: lesson.type
    })
  })
  return Object.values(grouped)
}

// Создание полного расписания 1-7 пара
const getFullDaySchedule = (dayData) => {
  const lessonTimes = {
    '1': '08:30-10:00',
    '2': '10:10-11:40',
    '3': '12:10-13:40',
    '4': '13:50-15:20',
    '5': '15:30-17:00',
    '6': '17:10-18:40',
    '7': '18:50-20:20'
  }
  
  const allPairs = []
  for (let i = 1; i <= 7; i++) {
    const existingLesson = groupedLessons.find(l => l.number === i.toString())
    if (existingLesson) {
      allPairs.push({
        ...existingLesson,
        time: lessonTimes[i.toString()]
      })
    } else {
      allPairs.push({
        number: i.toString(),
        time: lessonTimes[i.toString()],
        variants: [],
        isEmpty: true
      })
    }
  }
  return allPairs
}

// Определение специальности по названию группы
const getSpecialtyFromGroup = (groupName) => {
  const specialties = {
    'ИСП': { name: 'Информационные системы и программирование', icon: '💻' },
    'МТО': { name: 'Механо-техническое оборудование', icon: '⚙️' },
    'ТОА': { name: 'Техническое обслуживание автомобилей', icon: '🚗' },
    'СВ': { name: 'Сварочное производство', icon: '🔧' },
    'ТМ': { name: 'Технология машиностроения', icon: '🏭' },
    'ЭК': { name: 'Экономика и бухгалтерский учет', icon: '💼' },
  }
  
  for (const [prefix, data] of Object.entries(specialties)) {
    if (groupName.toUpperCase().startsWith(prefix)) {
      return { prefix, ...data }
    }
  }
  return { prefix: 'other', name: 'Другие', icon: '📚' }
}
```

### Training Page

**Файл**: `src/pages/Training.jsx`  
**Маршрут**: `/training`

Обучение и fine-tuning моделей на пользовательских данных.

**Функционал:**
- Просмотр собранных обучающих примеров
- Запуск обучения модели
- Отслеживание прогресса
- Метрики качества (loss, perplexity)
- История обучений

## 🎨 Стилизация

### Tailwind Configuration

**Файл**: `tailwind.config.js`

```js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          primary: '#0a0a0a',
          secondary: '#1a1a1a',
          tertiary: '#2a2a2a',
        },
        accent: {
          cyan: '#00d9ff',
          purple: '#a855f7',
          pink: '#ec4899',
        },
        text: {
          primary: '#ffffff',
          secondary: '#a0a0a0',
          muted: '#6b7280',
        },
        border: '#2d2d2d',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
```

### Global Styles

**Файл**: `src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  /* Glass Card Effect */
  .glass-card {
    @apply bg-primary-secondary/50 backdrop-blur-sm border border-border rounded-lg;
  }
  
  /* Primary Button */
  .btn-primary {
    @apply px-6 py-3 bg-gradient-to-r from-accent-cyan to-accent-purple 
           text-white font-medium rounded-lg 
           hover:opacity-90 transition-all duration-200
           disabled:opacity-50 disabled:cursor-not-allowed;
  }
  
  /* Secondary Button */
  .btn-secondary {
    @apply px-6 py-3 bg-primary-tertiary border border-border
           text-text-primary font-medium rounded-lg
           hover:bg-primary-tertiary/80 transition-all duration-200;
  }
  
  /* Input Field */
  .input-field {
    @apply w-full px-4 py-3 bg-primary-tertiary border border-border
           text-text-primary rounded-lg
           focus:outline-none focus:ring-2 focus:ring-accent-cyan
           placeholder:text-text-secondary;
  }
  
  /* Textarea */
  .textarea-field {
    @apply w-full px-4 py-3 bg-primary-tertiary border border-border
           text-text-primary rounded-lg resize-none
           focus:outline-none focus:ring-2 focus:ring-accent-cyan
           placeholder:text-text-secondary;
  }
}
```

### Responsive Design

**Мобильная навигация:**
```jsx
// Burger menu (видно только на мобильных)
<button className="md:hidden fixed top-4 left-4 z-50">
  <Menu size={24} />
</button>

// Sidebar с transition
<aside className={`
  w-64 fixed h-full z-40
  transition-transform duration-300
  ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
  md:translate-x-0
`}>
  {/* Navigation */}
</aside>

// Main content с адаптивными отступами
<main className="ml-0 md:ml-64 p-4 md:p-8 pt-16 md:pt-8">
  {children}
</main>
```

**Адаптивные сетки:**
```jsx
// Группы расписания
<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
  {groups.map(group => <GroupButton />)}
</div>

// Карточки функций
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {features.map(feature => <FeatureCard />)}
</div>
```

## 🔌 API интеграция

### Axios Configuration

**API Base URL:**
```jsx
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

### Примеры запросов

**GET request:**
```jsx
const fetchGroups = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/schedule/groups`)
    setGroups(response.data.groups || [])
  } catch (error) {
    console.error('Error:', error)
  }
}
```

**POST request с JSON:**
```jsx
const summarizeText = async (text, ratio) => {
  const response = await axios.post(
    `${API_URL}/api/llm/summarize`,
    { text, ratio },
    { headers: { 'Content-Type': 'application/json' } }
  )
  return response.data
}
```

**POST request с FormData:**
```jsx
const uploadFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await axios.post(
    `${API_URL}/api/parser/upload`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const percent = (progressEvent.loaded / progressEvent.total) * 100
        setUploadProgress(percent)
      }
    }
  )
  return response.data
}
```

## 🛠️ Разработка

### Запуск dev сервера

```bash
cd frontend
npm install
npm run dev
```

Приложение будет доступно на http://localhost:5173

### Production сборка

```bash
npm run build
npm run preview  # Preview production build
```

### Структура команд

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
  }
}
```

### Environment Variables

Создайте `.env` файл:

```env
VITE_API_URL=http://localhost:8000
```

**Важно:** Все переменные для Vite должны начинаться с `VITE_`

### Hot Module Replacement (HMR)

Vite обеспечивает мгновенное обновление при изменении:
- React компонентов
- CSS файлов
- Конфигурации

### ESLint Configuration

**Файл**: `.eslintrc.cjs`

```js
module.exports = {
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: '18.2' } },
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': 'warn',
    'react/prop-types': 'off',
  },
}
```

## 📱 Адаптивность

### Breakpoints

| Size | Min Width | Устройства |
|------|-----------|------------|
| `sm` | 640px | Мобильные (landscape) |
| `md` | 768px | Планшеты |
| `lg` | 1024px | Ноутбуки |
| `xl` | 1280px | Десктопы |
| `2xl` | 1536px | Широкие экраны |

### Примеры адаптации

**Скрытие элементов:**
```jsx
<div className="hidden md:block">Видно только на планшетах и выше</div>
<div className="block md:hidden">Видно только на мобильных</div>
```

**Адаптивные размеры:**
```jsx
<h1 className="text-2xl md:text-3xl lg:text-4xl">Заголовок</h1>
<div className="p-4 md:p-6 lg:p-8">Контент</div>
```

**Flex/Grid изменения:**
```jsx
<div className="flex-col md:flex-row">
<div className="grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
```

## 🐛 Debugging

### React DevTools

Установите расширение для Chrome/Firefox:
- Просмотр component tree
- Проверка props и state
- Profiling производительности

### Vite Debug

```bash
# Логирование в консоль
console.log('Debug:', variable)

# Network tab в DevTools
# Проверка API запросов

# Vite debug mode
DEBUG=vite:* npm run dev
```

### Распространённые проблемы

**CORS ошибки:**
```js
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

**404 на маршрутах в production:**
```js
// vite.config.js - добавьте fallback
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
}
```

## 🚀 Deployment

### Docker Production Build

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Nginx Configuration

```nginx
server {
  listen 80;
  server_name localhost;
  
  root /usr/share/nginx/html;
  index index.html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

---

**Автор**: Student Helper Team  
**Последнее обновление**: 19.11.2025
