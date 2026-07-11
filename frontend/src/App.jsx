import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Exam from './pages/Exam'
import ExamHistory from './pages/ExamHistory'
import WordManager from './pages/WordManager'

const Guard = ({ children }) => <ProtectedRoute>{children}</ProtectedRoute>
export default function App() {
  return <ConfigProvider locale={zhCN}><AuthProvider><BrowserRouter><Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route path="/" element={<Guard><Home /></Guard>} />
    <Route path="/exam/:examId" element={<Guard><Exam /></Guard>} />
    <Route path="/history" element={<Guard><ExamHistory /></Guard>} />
    <Route path="/words" element={<Guard><WordManager /></Guard>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></BrowserRouter></AuthProvider></ConfigProvider>
}
