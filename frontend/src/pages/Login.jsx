import { useState } from 'react'
import { Button, Card, Form, Input, Radio, Typography, message } from 'antd'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { userApi } from '../services/api'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()
  const submit = async (values) => {
    setLoading(true)
    try {
      const res = await userApi.login(values)
      login(res.data.token, res.data.user)
      message.success(`欢迎回来，${res.data.user.nickname}`)
      navigate('/')
    } catch (error) {
      message.error(error.message)
    } finally {
      setLoading(false)
    }
  }
  return <div className="page-container"><Card className="auth-card">
    <Typography.Title level={2}>WordMaster</Typography.Title>
    <Typography.Paragraph type="secondary">请选择身份并登录英语单词考试系统</Typography.Paragraph>
    <Form layout="vertical" initialValues={{ role: 'student' }} onFinish={submit}>
      <Form.Item label="登录身份" name="role" rules={[{ required: true }]}>
        <Radio.Group buttonStyle="solid"><Radio.Button value="student">学生登录</Radio.Button><Radio.Button value="teacher">教师登录</Radio.Button></Radio.Group>
      </Form.Item>
      <Form.Item label="用户名" name="username" rules={[{ required: true, message: '请输入用户名' }]}><Input /></Form.Item>
      <Form.Item label="密码" name="password" rules={[{ required: true, message: '请输入密码' }]}><Input.Password /></Form.Item>
      <Button type="primary" htmlType="submit" loading={loading} block>登录</Button>
    </Form>
    <Typography.Paragraph className="auth-link">没有账号？<Link to="/register">立即注册</Link></Typography.Paragraph>
  </Card></div>
}
