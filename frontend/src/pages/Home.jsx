import { BookOutlined, HistoryOutlined, LogoutOutlined } from '@ant-design/icons'
import { Button, Card, Col, Layout, Row, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { userApi } from '../services/api'

const { Header, Content } = Layout
const { Title, Text, Paragraph } = Typography

export default function Home() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    try {
      await userApi.logout()
    } catch {
      // ignore
    }
    logout()
    message.success('已退出登录')
    navigate('/login')
  }

  return (
    <Layout className="main-layout">
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#001529' }}>
        <Title level={4} style={{ color: '#fff', margin: 0 }}>
          WordMaster
        </Title>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Text style={{ color: '#fff' }}>你好，{user?.nickname || user?.username}</Text>
          <Button type="text" icon={<LogoutOutlined />} style={{ color: '#fff' }} onClick={handleLogout}>
            退出
          </Button>
        </div>
      </Header>
      <Content className="content-area">
        <Card style={{ marginTop: 24 }}>
          <Title level={3}>欢迎使用英语单词测试系统</Title>
          <Paragraph type="secondary">
            系统将从单词库中随机抽取题目，请根据英文单词填写中文释义。提交后系统将自动判卷并保存成绩。
          </Paragraph>
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col xs={24} sm={12}>
              <Card hoverable onClick={() => navigate('/exam')}>
                <BookOutlined style={{ fontSize: 32, color: '#1677ff' }} />
                <Title level={4} style={{ marginTop: 12 }}>开始考试</Title>
                <Text type="secondary">随机抽题，在线答题，自动判卷</Text>
              </Card>
            </Col>
            <Col xs={24} sm={12}>
              <Card hoverable onClick={() => navigate('/history')}>
                <HistoryOutlined style={{ fontSize: 32, color: '#52c41a' }} />
                <Title level={4} style={{ marginTop: 12 }}>考试记录</Title>
                <Text type="secondary">查看历史成绩与答题详情</Text>
              </Card>
            </Col>
          </Row>
        </Card>
      </Content>
    </Layout>
  )
}
