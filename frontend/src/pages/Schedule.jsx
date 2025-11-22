import { useState, useEffect } from 'react'
import { Calendar, Clock, MapPin, User, RefreshCw, ChevronDown, Search, Star } from 'lucide-react'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

const Schedule = () => {
  const { user } = useAuth()
  const [groups, setGroups] = useState([])
  const [selectedGroup, setSelectedGroup] = useState('')
  const [schedule, setSchedule] = useState(null)
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [currentDay, setCurrentDay] = useState(new Date().getDay())
  const [selectedSpecialty, setSelectedSpecialty] = useState('all')

  useEffect(() => {
    fetchGroups()
  }, [])

  // Автоматически загружаем расписание группы пользователя
  useEffect(() => {
    if (user?.group && groups.length > 0) {
      const userGroup = groups.find(g => g.name === user.group)
      if (userGroup && !selectedGroup) {
        fetchSchedule(userGroup.code)
      }
    }
  }, [user, groups])

  const fetchGroups = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/schedule/groups`
      )
      setGroups(response.data.groups || [])
    } catch (error) {
      console.error('Error fetching groups:', error)
    }
  }

  const fetchSchedule = async (groupCode) => {
    setLoading(true)
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/schedule/${groupCode}`
      )
      setSchedule(response.data)
      setSelectedGroup(groupCode)
    } catch (error) {
      console.error('Error fetching schedule:', error)
    } finally {
      setLoading(false)
    }
  }

  // Определение специальностей по префиксу группы
  const specialties = {
    'ИСП': { name: 'Информационные системы и программирование', icon: '💻' },
    'МТО': { name: 'Механо-техническое оборудование', icon: '⚙️' },
    'ТОА': { name: 'Техническое обслуживание автомобилей', icon: '🚗' },
    'СВ': { name: 'Сварочное производство', icon: '🔧' },
    'ТМ': { name: 'Технология машиностроения', icon: '🏭' },
    'ЭК': { name: 'Экономика и бухгалтерский учет', icon: '💼' },
  }

  const getSpecialtyFromGroup = (groupName) => {
    for (const [prefix, data] of Object.entries(specialties)) {
      if (groupName.toUpperCase().startsWith(prefix)) {
        return { prefix, ...data }
      }
    }
    return { prefix: 'other', name: 'Другие', icon: '📚' }
  }

  // Группировка групп по специальностям
  const groupedBySpecialty = groups.reduce((acc, group) => {
    const specialty = getSpecialtyFromGroup(group.name)
    if (!acc[specialty.prefix]) {
      acc[specialty.prefix] = {
        ...specialty,
        groups: []
      }
    }
    acc[specialty.prefix].groups.push(group)
    return acc
  }, {})

  // Фильтрация по поиску и выбранной специальности
  const filteredGroups = groups.filter(g => {
    const matchesSearch = g.name.toLowerCase().includes(searchQuery.toLowerCase())
    const specialty = getSpecialtyFromGroup(g.name)
    const matchesSpecialty = selectedSpecialty === 'all' || specialty.prefix === selectedSpecialty
    return matchesSearch && matchesSpecialty
  })

  const daysOfWeek = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
  
  // Группировка занятий по времени и номеру пары
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
    return Object.values(grouped).sort((a, b) => parseInt(a.number) - parseInt(b.number))
  }

  // Создание полного расписания с пустыми парами (1-7)
  const getFullDaySchedule = (dayData) => {
    if (!dayData) return []
    
    const lessons = dayData.lessons || []
    const groupedLessons = groupLessonsByTime(lessons)
    
    // Фиксированное расписание звонков СГТУ
    const lessonTimes = {
      '1': '08:30-10:00',
      '2': '10:10-11:40', 
      '3': '12:10-13:40',
      '4': '13:50-15:20',
      '5': '15:30-17:00',
      '6': '17:10-18:40',
      '7': '18:50-20:20'
    }
    
    // Создаем массив всех пар (1-7)
    const allPairs = []
    
    for (let i = 1; i <= 7; i++) {
      const existingLesson = groupedLessons.find(l => l.number === i.toString())
      if (existingLesson) {
        // Используем фиксированное время вместо того что с сайта
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">📅 Расписание занятий</h1>
        <p className="text-text-secondary">
          Удобное расписание для студентов СГТУ
        </p>
      </div>

      {/* Выбор группы */}
      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <User size={20} className="text-accent-cyan" />
          Выберите группу
        </h2>

        {/* Поиск */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" size={20} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Поиск группы... (например, ИСП-12)"
            className="input-field pl-10"
          />
        </div>

        {/* Фильтр по специальностям */}
        {groups.length > 0 && Object.keys(groupedBySpecialty).length > 1 && (
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedSpecialty('all')}
              className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                selectedSpecialty === 'all'
                  ? 'bg-accent-cyan text-primary-primary'
                  : 'bg-primary-tertiary text-text-secondary hover:bg-primary-tertiary/80'
              }`}
            >
              Все
            </button>
            {Object.entries(groupedBySpecialty).map(([prefix, data]) => (
              <button
                key={prefix}
                onClick={() => setSelectedSpecialty(prefix)}
                className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                  selectedSpecialty === prefix
                    ? 'bg-accent-cyan text-primary-primary'
                    : 'bg-primary-tertiary text-text-secondary hover:bg-primary-tertiary/80'
                }`}
              >
                <span className="hidden sm:inline">{data.icon} </span>
                {prefix}
                <span className="ml-1 text-xs opacity-70">({data.groups.length})</span>
              </button>
            ))}
          </div>
        )}

        {/* Список групп */}
        {groups.length > 0 ? (
          <>
            {selectedSpecialty === 'all' ? (
              // Группировка по специальностям
              <div className="space-y-6">
                {Object.entries(groupedBySpecialty).map(([prefix, data]) => {
                  const specialtyGroups = data.groups.filter(g =>
                    g.name.toLowerCase().includes(searchQuery.toLowerCase())
                  )
                  
                  if (specialtyGroups.length === 0) return null

                  return (
                    <div key={prefix}>
                      <h3 className="text-sm font-semibold text-text-secondary mb-3 flex items-center gap-2">
                        <span className="text-lg">{data.icon}</span>
                        <span>{data.name}</span>
                        <span className="text-xs opacity-50">({specialtyGroups.length})</span>
                      </h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                        {specialtyGroups.map((group) => {
                          const isUserGroup = user?.group === group.name
                          return (
                            <button
                              key={group.code}
                              onClick={() => fetchSchedule(group.code)}
                              className={`px-3 py-2.5 rounded-lg border transition-all duration-200 text-sm font-medium relative ${
                                selectedGroup === group.code
                                  ? 'bg-accent-cyan/20 border-accent-cyan text-accent-cyan'
                                  : isUserGroup
                                  ? 'bg-accent-purple/20 border-accent-purple text-accent-purple'
                                  : 'bg-primary-tertiary border-border text-text-secondary hover:border-accent-cyan/50 hover:text-text-primary'
                              }`}
                            >
                              {isUserGroup && (
                                <Star size={12} className="absolute top-1 right-1 fill-current" />
                              )}
                              {group.name}
                              {isUserGroup && (
                                <span className="block text-[10px] opacity-70 mt-0.5">Ваша группа</span>
                              )}
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              // Плоский список для выбранной специальности
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                {filteredGroups.map((group) => {
                  const isUserGroup = user?.group === group.name
                  return (
                    <button
                      key={group.code}
                      onClick={() => fetchSchedule(group.code)}
                      className={`px-4 py-3 rounded-lg border transition-all duration-200 text-sm font-medium relative ${
                        selectedGroup === group.code
                          ? 'bg-accent-cyan/20 border-accent-cyan text-accent-cyan'
                          : isUserGroup
                          ? 'bg-accent-purple/20 border-accent-purple text-accent-purple'
                          : 'bg-primary-tertiary border-border text-text-secondary hover:border-accent-cyan/50 hover:text-text-primary'
                      }`}
                    >
                      {isUserGroup && (
                        <Star size={12} className="absolute top-1 right-1 fill-current" />
                      )}
                      {group.name}
                      {isUserGroup && (
                        <span className="block text-[10px] opacity-70 mt-0.5">Ваша группа</span>
                      )}
                    </button>
                  )
                })}
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-8 text-text-secondary">
            <RefreshCw className="animate-spin mx-auto mb-2" size={24} />
            <p>Загрузка списка групп...</p>
          </div>
        )}
      </div>

      {/* Расписание */}
      {loading && (
        <div className="glass-card p-12 text-center">
          <RefreshCw className="animate-spin mx-auto mb-4 text-accent-cyan" size={32} />
          <p className="text-text-secondary">Загрузка расписания...</p>
        </div>
      )}

      {schedule && !loading && (
        <div className="space-y-4">
          {/* Информация о группе */}
          <div className="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-accent-cyan">{schedule.group_name}</h3>
              <p className="text-xs sm:text-sm text-text-secondary">
                Последнее обновление: {schedule.last_updated || 'неизвестно'}
              </p>
            </div>
            <button
              onClick={() => fetchSchedule(selectedGroup)}
              className="btn-secondary flex items-center gap-2 w-full sm:w-auto"
            >
              <RefreshCw size={16} />
              <span className="text-sm">Обновить</span>
            </button>
          </div>

          {/* Дни недели */}
          {schedule?.schedule_days?.map((dayData, index) => {
            const dayLessons = getFullDaySchedule(dayData)
            const hasLessons = dayLessons.some(l => !l.isEmpty)
            
            // Проверка по реальной дате
            const today = new Date()
            const todayStr = `${String(today.getDate()).padStart(2, '0')}.${String(today.getMonth() + 1).padStart(2, '0')}.${today.getFullYear()}`
            const isToday = dayData.date === todayStr

            return (
              <div
                key={`${dayData.date}-${index}`}
                className={`glass-card overflow-hidden ${
                  isToday ? 'ring-2 ring-accent-cyan' : ''
                }`}
              >
                <div className={`p-3 sm:p-4 border-b border-border ${
                  isToday ? 'bg-accent-cyan/10' : 'bg-primary-tertiary'
                }`}>
                  <h3 className="text-base sm:text-lg font-semibold flex items-center gap-2 flex-wrap">
                    <Calendar size={18} className={isToday ? 'text-accent-cyan' : 'text-text-secondary'} />
                    <span>{dayData.day}</span>
                    <span className="text-xs sm:text-sm text-text-secondary font-normal">
                      {dayData.date}
                    </span>
                    {isToday && (
                      <span className="text-xs bg-accent-cyan text-primary-primary px-2 py-0.5 rounded-full">
                        Сегодня
                      </span>
                    )}
                  </h3>
                </div>

                <div className="p-3 sm:p-4">
                  {hasLessons ? (
                    <div className="space-y-2 sm:space-y-3">
                      {dayLessons.map((lesson, lessonIndex) => (
                        <div
                          key={lessonIndex}
                          className={`p-3 sm:p-4 rounded-lg border transition-colors ${
                            lesson.isEmpty 
                              ? 'bg-primary-tertiary/50 border-border/50 opacity-50' 
                              : 'bg-primary-secondary border-border hover:border-accent-cyan/30'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-2 gap-2">
                            <div className="flex items-center gap-2">
                              <Clock size={14} className={lesson.isEmpty ? 'text-text-secondary' : 'text-accent-cyan'} />
                              <span className={`text-sm sm:text-base font-semibold ${lesson.isEmpty ? 'text-text-secondary' : 'text-accent-cyan'}`}>
                                {lesson.time}
                              </span>
                            </div>
                            <span className="text-xs bg-primary-tertiary px-2 py-0.5 rounded shrink-0">
                              {lesson.number} пара
                            </span>
                          </div>

                          {lesson.isEmpty ? (
                            <p className="text-sm text-text-secondary italic">Нет занятий</p>
                          ) : (
                            <div className="space-y-2 sm:space-y-3">
                              {lesson.variants.map((variant, variantIndex) => (
                                <div key={variantIndex} className={variantIndex > 0 ? 'pt-2 sm:pt-3 border-t border-border' : ''}>
                                  {lesson.variants.length > 1 && (
                                    <span className={`text-xs px-2 py-0.5 rounded mb-1.5 inline-block ${
                                      user?.subgroup === variantIndex + 1
                                        ? 'bg-accent-purple/20 text-accent-purple'
                                        : 'bg-accent-cyan/20 text-accent-cyan'
                                    }`}>
                                      Подгруппа {variantIndex + 1}
                                      {user?.subgroup === variantIndex + 1 && ' (ваша)'}
                                    </span>
                                  )}
                                  <h4 className="font-medium text-sm sm:text-base text-text-primary mb-1.5">
                                    {variant.subject}
                                  </h4>
                                  <div className="space-y-1 text-xs sm:text-sm text-text-secondary">
                                    {variant.teacher && (
                                      <div className="flex items-center gap-2">
                                        <User size={12} className="shrink-0" />
                                        <span className="break-words">{variant.teacher}</span>
                                      </div>
                                    )}
                                    {variant.room && (
                                      <div className="flex items-center gap-2">
                                        <MapPin size={12} className="shrink-0" />
                                        <span>{variant.room}</span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-text-secondary">
                      <Calendar size={32} className="mx-auto mb-2 opacity-50" />
                      <p>Нет занятий</p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {!schedule && !loading && groups.length > 0 && (
        <div className="glass-card p-12 text-center">
          <Calendar size={48} className="mx-auto mb-4 text-text-secondary opacity-50" />
          <p className="text-text-secondary">Выберите группу для просмотра расписания</p>
        </div>
      )}
    </div>
  )
}

export default Schedule
