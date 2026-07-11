import { ArrowLeftOutlined, CheckCircleOutlined, CloseCircleOutlined, HomeOutlined } from '@ant-design/icons'
import { Button, Card, Descriptions, Layout, List, Space, Tag, Typography } from 'antd'
import { useLocation, useNavigate } from 'react-router-dom'
import { formatDateTime, formatDuration } from '../utils/time'

const { Header, Content } = Layout
const { Title, Text } = Typography

export default function ExamResult() {
  const navigate = useNavigate()
  const location = useLocation()
  const result = location.state?.result

  if (!result) {
    return (
      <div className="page-container">
        <Card>
          <Text>暂无考试结果，请先完成考试。</Text>
          <Button type="primary" style={{ marginTop: 16 }} onClick={() => navigate('/exam')}>
            开始考试
          </Button>
        </Card>
      </div>
    )
  }

  const { score, correct_count, total_questions, answers, start_time, end_time, duration_seconds } = result

  return (
    <Layout className="main-layout">
      <Header style={{ display: 'flex', alignItems: 'center', background: '#001529' }}>
        <Title level={4} style={{ color: '#fff', margin: 0 }}>
          考试结果
        </Title>
      </Header>
      <Content className="content-area">
        <Card style={{ marginTop: 24 }}>
          <Descriptions bordered size="small" column={2} style={{ marginBottom: 24 }}>
            <Descriptions.Item label="开始时间">{formatDateTime(start_time)}</Descriptions.Item>
            <Descriptions.Item label="结束时间">{formatDateTime(end_time)}</Descriptions.Item>
            <Descriptions.Item label="用时" span={2}>{formatDuration(duration_seconds)}</Descriptions.Item>
          </Descriptions>
          <div className="result-score">
            <div className="score-value">{score}</div>
            <Text type="secondary">分</Text>
            <Title level={4} style={{ marginTop: 16 }}>
              答对 {correct_count} / {total_questions} 题
            </Title>
          </div>
          <List
            header={<Title level={5}>答题详情</Title>}
            dataSource={answers}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  avatar={
                    item.is_correct ? (
                      <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                    ) : (
                      <CloseCircleOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />
                    )
                  }
                  title={
                    <Space wrap>
                      <Tag color="purple">{item.question_type_label || '题目'}</Tag>
                      <Text strong>{item.prompt || item.word}</Text>
                      <Tag color={item.is_correct ? 'success' : 'error'}>
                        {item.is_correct ? '正确' : '错误'}
                      </Tag>
                    </Space>
                  }
                  description={
                    <>
                      <div>你的答案：{item.user_answer || '（未作答）'}</div>
                      {!item.is_correct && (
                        <div>正确答案：{item.correct_answer || item.correct_meaning}</div>
                      )}
                    </>
                  }
                />
              </List.Item>
            )}
          />
          <Space style={{ marginTop: 24 }}>
            <Button type="primary" icon={<HomeOutlined />} onClick={() => navigate('/')}>
              返回首页
            </Button>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/exam')}>
              再考一次
            </Button>
          </Space>
        </Card>
      </Content>
    </Layout>
  )
}
