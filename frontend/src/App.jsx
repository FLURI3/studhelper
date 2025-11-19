import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Home from './pages/Home'
import Parser from './pages/Parser'
import TextShortener from './pages/TextShortener'
import Analyzer from './pages/Analyzer'
import QuestionGenerator from './pages/QuestionGenerator'
import Documents from './pages/Documents'
import Training from './pages/Training'
import Schedule from './pages/Schedule'

function App() {
  return (
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
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
