import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout/Layout'
import Home from './pages/Home'
import Parser from './pages/Parser'
import TextShortener from './pages/TextShortener'
import Analyzer from './pages/Analyzer'
import QuestionGenerator from './pages/QuestionGenerator'
import Documents from './pages/Documents'
import Training from './pages/Training'
import Schedule from './pages/Schedule'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/parser" element={<Parser />} />
            <Route path="/shortener" element={<TextShortener />} />
            <Route path="/analyzer" element={<Analyzer />} />
            <Route path="/questions" element={<QuestionGenerator />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/training" element={<Training />} />
            <Route path="/schedule" element={<Schedule />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  )
}

export default App
