import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { User, Save, BookOpen } from 'lucide-react'
import axios from 'axios'

const Profile = () => {
  const { user, updateProfile } = useAuth()
  const [formData, setFormData] = useState({
    full_name: '',
    group: '',
    subgroup: ''
  })
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        group: user.group || '',
        subgroup: user.subgroup || ''
      })
    }
  }, [user])

  // Загрузка списка групп
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/schedule/groups`)
        setGroups(response.data.groups || [])
      } catch (err) {
        console.error('Ошибка загрузки групп:', err)
      }
    }
    fetchGroups()
  }, [API_URL])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: name === 'subgroup' ? (value ? parseInt(value) : '') : value
    })
    setError('')
    setSuccess(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setLoading(true)

    const result = await updateProfile({
      full_name: formData.full_name || null,
      group: formData.group || null,
      subgroup: formData.subgroup ? parseInt(formData.subgroup) : null
    })

    setLoading(false)

    if (result.success) {
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } else {
      setError(result.error)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="glass-card p-8">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-accent-cyan to-accent-purple rounded-full flex items-center justify-center">
            <User size={32} className="text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Профиль</h1>
            <p className="text-text-secondary">@{user?.username}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email (только для чтения) */}
          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="input-field opacity-60 cursor-not-allowed"
            />
          </div>

          {/* Полное имя */}
          <div>
            <label className="block text-sm font-medium mb-2">Полное имя</label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="input-field"
              placeholder="Иван Иванов"
            />
          </div>

          {/* Группа */}
          <div>
            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
              <BookOpen size={18} />
              Группа
            </label>
            <select
              name="group"
              value={formData.group}
              onChange={handleChange}
              className="input-field"
            >
              <option value="">Выберите группу</option>
              {groups.map((group) => (
                <option key={group.code} value={group.name}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          {/* Подгруппа */}
          <div>
            <label className="block text-sm font-medium mb-2">Подгруппа</label>
            <select
              name="subgroup"
              value={formData.subgroup}
              onChange={handleChange}
              className="input-field"
            >
              <option value="">Не указана</option>
              <option value="1">1</option>
              <option value="2">2</option>
            </select>
            <p className="text-sm text-text-secondary mt-2">
              Некоторые пары разделены на подгруппы
            </p>
          </div>

          {/* Сообщения */}
          {error && (
            <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="p-3 bg-green-500/20 border border-green-500/50 rounded-lg text-green-400 text-sm">
              Профиль успешно обновлён!
            </div>
          )}

          {/* Кнопка сохранения */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            <Save size={20} />
            {loading ? 'Сохранение...' : 'Сохранить изменения'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Profile
