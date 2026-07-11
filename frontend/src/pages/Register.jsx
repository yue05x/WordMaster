import { useState } from 'react'
import { Button, Card, Form, Input, Radio, Typography, message } from 'antd'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { userApi } from '../services/api'

export default function Register() {
  const [loading, setLoading] = useState(false)
  const [role, setRole] = useState('student')
  const navigate = useNavigate()
  const { login } = useAuth()
  const submit = async (values) => {
    setLoading(true)
    try {
      const res = await userApi.register(values)
      login(res.data.token, res.data.user)
      message.success(`${res.data.user.role === 'teacher' ? '教师' : '学生'}账号注册成功`)
      navigate('/')
    } catch (error) {
      message.error(error.message)
    } finally {
      setLoading(false)
    }
  }
  return <div className="page-container"><Card className="auth-card">
    <Typography.Title level={2}>创建账号</Typography.Title>
    <Form layout="vertical" initialValues={{ role: 'student' }} onFinish={submit}>
      <Form.Item label="注册身份" name="role" rules={[{ required: true }]}>
        <Radio.Group buttonStyle="solid" onChange={(e) => setRole(e.target.value)}><Radio.Button value="student">学生</Radio.Button><Radio.Button value="teacher">教师</Radio.Button></Radio.Group>
      </Form.Item>
      <Form.Item label="用户名" name="username" rules={[{ required: true, min: 3, message: '用户名至少3位' }]}><Input /></Form.Item>
      <Form.Item label="昵称" name="nickname"><Input /></Form.Item>
      <Form.Item label="密码" name="password" rules={[{ required: true, min: 6, message: '密码至少6位' }]}><Input.Password /></Form.Item>
      {role === 'teacher' && <Form.Item label="教师邀请码" name="teacher_code" rules={[{ required: true, message: '请输入教师邀请码' }]}><Input.Password placeholder="开发环境默认 teacher123" /></Form.Item>}
      <Button type="primary" htmlType="submit" loading={loading} block>注册</Button>
    </Form>
    <Typography.Paragraph className="auth-link">已有账号？<Link to="/login">返回登录</Link></Typography.Paragraph>
  </Card></div>
}
