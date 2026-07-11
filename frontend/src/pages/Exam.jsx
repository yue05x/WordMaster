import { useEffect, useRef, useState } from 'react'
import { ArrowLeftOutlined, CheckOutlined, ClockCircleOutlined } from '@ant-design/icons'
import {
  Alert,
  Button,
  Card,
  Divider,
  Form,
  Input,
  Layout,
  Modal,
  Progress,
  Radio,
  Space,
  Statistic,
  Tag,
  Typography,
  message,
} from 'antd'
import { useNavigate } from 'react-router-dom'
import { examApi } from '../services/api'
import { formatCountdown, formatDateTime } from '../utils/time'

const { Header, Content } = Layout
const { Title, Text } = Typography

const CHOICE_TYPES = new Set(['choice_en_to_cn', 'choice_cn_to_en'])
const EN_TYPES = new Set(['en_to_cn', 'choice_en_to_cn'])

function QuestionBody({ question, index }) {
  const fieldName = `answer_${index}`
  const isChoice = CHOICE_TYPES.has(question.question_type) && question.options?.length > 1

  if (isChoice) {
    return (
      <Form.Item
        name={fieldName}
        label="请选择正确答案"
        rules={[{ required: true, message: '请选择答案' }]}
      >
        <Radio.Group>
          <Space direction="vertical">
            {question.options.map((option) => (
              <Radio key={option} value={option}>
                {option}
              </Radio>
            ))}
          </Space>
        </Radio.Group>
      </Form.Item>
    )
  }

  const isEnToCn = EN_TYPES.has(question.question_type)
  return (
    <Form.Item
      name={fieldName}
      label={isEnToCn ? '请填写中文释义' : '请填写英文单词'}
      rules={[{ required: true, message: '请填写答案' }]}
    >
      <Input
        placeholder={isEnToCn ? '输入中文释义' : '输入英文单词'}
        size="large"
      />
    </Form.Item>
  )
}

export default function Exam() {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [examId, setExamId] = useState(null)
  const [questions, setQuestions] = useState([])
  const [startTime, setStartTime] = useState(null)
  const [durationMinutes, setDurationMinutes] = useState(30)
  const [remainingSeconds, setRemainingSeconds] = useState(null)
  const [formTick, setFormTick] = useState(0)
  const autoSubmittedRef = useRef(false)
  const examIdRef = useRef(null)
  const questionsRef = useRef([])

  useEffect(() => {
    examIdRef.current = examId
  }, [examId])

  useEffect(() => {
    questionsRef.current = questions
  }, [questions])

  useEffect(() => {
    startExam()
  }, [])

  useEffect(() => {
    if (!startTime || durationMinutes == null) return undefined

    const endTimestamp = new Date(startTime.endsWith('Z') ? startTime : `${startTime}Z`).getTime()
      + durationMinutes * 60 * 1000

    const timer = window.setInterval(() => {
      const left = Math.max(0, Math.floor((endTimestamp - Date.now()) / 1000))
      setRemainingSeconds(left)

      if (left === 0 && !autoSubmittedRef.current) {
        autoSubmittedRef.current = true
        message.warning('考试时间到，系统将自动提交试卷')
        submitExam(true)
      }
    }, 1000)

    return () => window.clearInterval(timer)
  }, [startTime, durationMinutes])

  const startExam = async (count) => {
    setLoading(true)
    autoSubmittedRef.current = false
    try {
      const res = await examApi.start(count)
      setExamId(res.data.exam_id)
      setQuestions(res.data.questions)
      setStartTime(res.data.start_time)
      setDurationMinutes(res.data.duration_minutes || 30)
      form.resetFields()
    } catch (err) {
      message.error(err.message)
    } finally {
      setLoading(false)
    }
  }

  const submitExam = async (autoSubmit = false) => {
    if (submitting) return

    const runSubmit = async () => {
      setSubmitting(true)
      try {
        const values = form.getFieldsValue()
        const currentQuestions = questionsRef.current
        const answers = currentQuestions.map((q, index) => ({
          word_id: q.word_id,
          question_type: q.question_type,
          user_answer: values[`answer_${index}`] || '',
        }))
        const res = await examApi.submit(examIdRef.current, answers)
        navigate('/exam/result', { state: { result: res.data } })
      } catch (err) {
        message.error(err.message)
        autoSubmittedRef.current = false
      } finally {
        setSubmitting(false)
      }
    }

    if (autoSubmit) {
      await runSubmit()
      return
    }

    Modal.confirm({
      title: '确认提交试卷？',
      content: '提交后将自动判卷，无法修改答案。',
      okText: '确认提交',
      cancelText: '继续答题',
      onOk: runSubmit,
    })
  }

  const handleSubmit = () => {
    form.validateFields()
      .then(() => submitExam(false))
      .catch(() => message.warning('请完成所有题目'))
  }

  const answeredCount = questions.filter((_, index) => {
    void formTick
    const val = form.getFieldValue(`answer_${index}`)
    return val != null && String(val).trim() !== ''
  }).length

  const isTimeWarning = remainingSeconds != null && remainingSeconds <= 300

  return (
    <Layout className="main-layout">
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#001529' }}>
        <Space>
          <Button type="text" icon={<ArrowLeftOutlined />} style={{ color: '#fff' }} onClick={() => navigate('/')}>
            返回
          </Button>
          <Title level={4} style={{ color: '#fff', margin: 0 }}>
            在线考试
          </Title>
        </Space>
        <Space size="large">
          <Text style={{ color: '#fff' }}>已答 {answeredCount} / {questions.length}</Text>
          {remainingSeconds != null && (
            <Text style={{ color: isTimeWarning ? '#ff7875' : '#fff' }}>
              <ClockCircleOutlined /> 剩余 {formatCountdown(remainingSeconds)}
            </Text>
          )}
        </Space>
      </Header>
      <Content className="content-area">
        <Card loading={loading} style={{ marginTop: 24 }}>
          {!loading && questions.length > 0 && (
            <>
              <Space size="large" wrap style={{ marginBottom: 16 }}>
                <Statistic title="开始时间" value={formatDateTime(startTime)} />
                <Statistic title="考试时长" value={`${durationMinutes} 分钟`} />
                <Statistic
                  title="剩余时间"
                  value={formatCountdown(remainingSeconds)}
                  valueStyle={{ color: isTimeWarning ? '#cf1322' : '#1677ff' }}
                />
              </Space>

              {isTimeWarning && (
                <Alert
                  type="warning"
                  showIcon
                  message="考试即将结束，请尽快完成并提交试卷"
                  style={{ marginBottom: 16 }}
                />
              )}

              <Progress
                percent={Math.round((answeredCount / questions.length) * 100)}
                style={{ marginBottom: 24 }}
              />
              <Form
                form={form}
                layout="vertical"
                onValuesChange={() => setFormTick((value) => value + 1)}
              >
                {questions.map((q, index) => {
                  const showSection = index === 0 || questions[index - 1].question_type !== q.question_type
                  return (
                    <div key={`${q.word_id}-${index}`}>
                      {showSection && (
                        <Divider orientation="left">
                          <Title level={5} style={{ margin: 0 }}>
                            {q.question_type_label}
                          </Title>
                        </Divider>
                      )}
                      <div className="exam-question">
                        <Space style={{ marginBottom: 8 }} wrap>
                          <Tag color="blue">第 {index + 1} 题</Tag>
                          {q.level && <Tag>{q.level}</Tag>}
                        </Space>
                        <Title level={4}>
                          {q.prompt}
                          {q.phonetic && (
                            <Text type="secondary" style={{ fontSize: 16, marginLeft: 8 }}>
                              {q.phonetic}
                            </Text>
                          )}
                        </Title>
                        <QuestionBody question={q} index={index} />
                      </div>
                    </div>
                  )
                })}
              </Form>
              <Button
                type="primary"
                size="large"
                icon={<CheckOutlined />}
                loading={submitting}
                onClick={handleSubmit}
                block
              >
                提交试卷
              </Button>
            </>
          )}
        </Card>
      </Content>
    </Layout>
  )
}
