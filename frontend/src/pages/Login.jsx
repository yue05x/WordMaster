import { useState } from 'react'
import { Button, Card, Form, Input, Typography, message } from 'antd'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { userApi } from '../services/api'

export default function Login() {
  const [loading, setLoading] = useState(false); const navigate = useNavigate(); const { login } = useAuth()
  const submit = async (values) => { setLoading(true); try { const res = await userApi.login(values); login(res.data.token, res.data.user); navigate('/') } catch (e) { message.error(e.message) } finally { setLoading(false) } }
  return <div className="page-container"><Card className="auth-card">
    <Typography.Title level={2}>WordMaster</Typography.Title><Typography.Paragraph type="secondary">英语单词考试系统</Typography.Paragraph>
    <Form layout="vertical" onFinish={submit}><Form.Item label="用户名" name="username" rules={[{ required: true }]}><Input /></Form.Item>
    <Form.Item label="密码" name="password" rules={[{ required: true }]}><Input.Password /></Form.Item>
    <Button type="primary" htmlType="submit" loading={loading} block>登录</Button></Form>
    <Typography.Paragraph className="auth-link">没有账号？<Link to="/register">注册</Link></Typography.Paragraph>
  </Card></div>
}
