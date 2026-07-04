import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './auth/ProtectedRoute.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Jobs from './pages/Jobs.jsx'
import JobDetail from './pages/JobDetail.jsx'
import Generate from './pages/Generate.jsx'
import SkillGap from './pages/SkillGap.jsx'
import InterviewPrep from './pages/InterviewPrep.jsx'
import UploadMemory from './pages/UploadMemory.jsx'
import MemoryLibrary from './pages/MemoryLibrary.jsx'
import Lifecycle from './pages/Lifecycle.jsx'
import Settings from './pages/Settings.jsx'

const protect = (el) => <ProtectedRoute>{el}</ProtectedRoute>

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/dashboard" element={protect(<Dashboard />)} />
      <Route path="/jobs" element={protect(<Jobs />)} />
      <Route path="/jobs/:id" element={protect(<JobDetail />)} />
      <Route path="/generate" element={protect(<Generate />)} />
      <Route path="/skill-gap" element={protect(<SkillGap />)} />
      <Route path="/interview-prep" element={protect(<InterviewPrep />)} />
      <Route path="/memory/upload" element={protect(<UploadMemory />)} />
      <Route path="/memory/library" element={protect(<MemoryLibrary />)} />
      <Route path="/lifecycle" element={protect(<Lifecycle />)} />
      <Route path="/settings" element={protect(<Settings />)} />

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
