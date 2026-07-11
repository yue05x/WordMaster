import { useState } from 'react'
import { Button, Card, Form, Input, Radio, Typography, message } from 'antd'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { userApi } from '../services/api'

export default function Register() {
  const [loading, setLoading] = useState(false); const [role, setRole] = useState('student'); const navigate = useNavigate(); const { login } = useAuth()
  const submit = async (values) => { setLoading(true); try { const res = await userApi.register(values); login(res.data.token, res.data.user); navigate('/') } catch (e) { message.error(e.message) } finally { setLoading(false) } }
  return <div className="page-container"><Card className="auth-card"><Typography.Title level={2}>创建账号</Typography.Title>
    <Form layout="vertical" initialValues={{ role: 'student' }} onFinish={submit}>
      <Form.Item label="用户名" name="username" rules={[{ required: true, min: 3 }]}><Input /></Form.Item>
      <Form.Item label="昵称" name="nickname"><Input /></Form.Item>
      <Form.Item label="密码" name="password" rules={[{ required: true, min: 6 }]}><Input.Password /></Form.Item>
      <Form.Item label="身份" name="role"><Radio.Group onChange={(e) => setRole(e.target.value)}><Radio value="student">学生</Radio><Radio value="teacher">教师</Radio></Radio.Group></Form.Item>
      {role === 'teacher' && <Form.Item label="教师邀请码" name="teacher_code" rules={[{ required: true }]}><Input.Password placeholder="默认演示码 teacher123" /></Form.Item>}
      <Button type="primary" htmlType="submit" loading={loading} block>注册</Button>
    </Form><Typography.Paragraph className="auth-link">已有账号？<Link to="/login">登录</Link></Typography.Paragraph>
  </Card></div>
}
