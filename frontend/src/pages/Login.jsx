import { useState } from 'react'
import { LockOutlined, MailOutlined, UserOutlined } from '@ant-design/icons'
import { Button, Card, Form, Input, Typography, message } from 'antd'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { userApi } from '../services/api'

const { Title, Text } = Typography

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const res = await userApi.login(values)
      login(res.data.token, res.data.user)
      message.success('登录成功')
      navigate('/')
    } catch (err) {
      message.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <Card className="auth-card">
        <Title level={3} style={{ textAlign: 'center', marginBottom: 8 }}>
          WordMaster
        </Title>
        <Text type="secondary" style={{ display: 'block', textAlign: 'center', marginBottom: 24 }}>
          英语单词测试系统
        </Text>
        <Form form={form} onFinish={onFinish} size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登录
            </Button>
          </Form.Item>
        </Form>
        <Text style={{ textAlign: 'center', display: 'block' }}>
          还没有账号？ <Link to="/register">立即注册</Link>
        </Text>
      </Card>
    </div>
  )
}
