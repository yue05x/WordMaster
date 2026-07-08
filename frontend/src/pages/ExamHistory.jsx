import { useEffect, useState } from 'react'
import { ArrowLeftOutlined, EyeOutlined } from '@ant-design/icons'
import { Button, Card, Layout, Space, Table, Tag, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { examApi } from '../services/api'
import { formatDateTime, formatDuration } from '../utils/time'

const { Header, Content } = Layout
const { Title } = Typography

export default function ExamHistory() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [records, setRecords] = useState([])

  useEffect(() => {
    loadRecords()
  }, [])

  const loadRecords = async () => {
    setLoading(true)
    try {
      const res = await examApi.getRecords()
      setRecords(res.data)
    } catch (err) {
      message.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  const viewDetail = async (examId) => {
    try {
      const res = await examApi.getDetail(examId)
      navigate('/exam/result', { state: { result: res.data } })
    } catch (err) {
      message.error(err.message)
    }
  }

  const columns = [
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      render: (text) => formatDateTime(text),
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      render: (text) => formatDateTime(text),
    },
    {
      title: '用时',
      dataIndex: 'duration_seconds',
      key: 'duration_seconds',
      render: (seconds) => formatDuration(seconds),
    },
    {
      title: '总题数',
      dataIndex: 'total_questions',
      key: 'total_questions',
    },
    {
      title: '正确数',
      dataIndex: 'correct_count',
      key: 'correct_count',
    },
    {
      title: '得分',
      dataIndex: 'score',
      key: 'score',
      render: (score) => (
        <Tag color={score >= 60 ? 'success' : 'error'}>{score} 分</Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => viewDetail(record.id)}>
          查看详情
        </Button>
      ),
    },
  ]

  return (
    <Layout className="main-layout">
      <Header style={{ display: 'flex', alignItems: 'center', background: '#001529' }}>
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} style={{ color: '#fff' }} onClick={() => navigate('/')}>
            返回
          </Button>
          <Title level={4} style={{ color: '#fff', margin: 0 }}>
            考试记录
          </Title>
        </Space>
      </Header>
      <Content className="content-area">
        <Card style={{ marginTop: 24 }}>
          <Table
            rowKey="id"
            loading={loading}
            columns={columns}
            dataSource={records}
            pagination={{ pageSize: 10 }}
            locale={{ emptyText: '暂无考试记录' }}
          />
        </Card>
      </Content>
    </Layout>
  )
}
