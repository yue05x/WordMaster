import { useEffect, useRef, useState } from 'react'
import { Button, Card, Form, Input, Modal, Progress, Space, Typography, message } from 'antd'
import { useNavigate, useParams } from 'react-router-dom'
import { examApi } from '../services/api'

export default function Exam() {
  const { examId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [left, setLeft] = useState(0)
  const [answered, setAnswered] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const submittedRef = useRef(false)
  const [form] = Form.useForm()
  const draftKey = `wordmaster-exam-draft-${examId}`

  useEffect(() => {
    examApi.start(examId).then((res) => {
      setData(res.data)
      setLeft(Math.max(0, Math.floor((new Date(res.data.deadline) - Date.now()) / 1000)))
      const draft = JSON.parse(localStorage.getItem(draftKey) || '{}')
      form.setFieldsValue(draft)
      setAnswered(Object.values(draft).filter((v) => String(v || '').trim()).length)
    }).catch((error) => { message.error(error.message); navigate('/') })
  }, [examId])

  const submitValues = async (values, automatic = false) => {
    if (!data || submittedRef.current) return
    submittedRef.current = true
    setSubmitting(true)
    try {
      const answers = data.questions.map((q) => ({ question_id: q.question_id, answer: values[q.question_id] || '' }))
      const res = await examApi.submit(data.attempt_id, answers)
      localStorage.removeItem(draftKey)
      Modal.success({ title: automatic ? '考试时间到，系统已自动交卷' : '交卷成功', content: `得分 ${res.data.score}，答对 ${res.data.correct_count}/${res.data.total_questions} 题`, onOk: () => navigate('/history') })
    } catch (error) {
      submittedRef.current = false
      message.error(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  useEffect(() => {
    if (!data) return
    const timer = setInterval(() => setLeft((value) => {
      if (value <= 1) {
        clearInterval(timer)
        submitValues(form.getFieldsValue(), true)
        return 0
      }
      return value - 1
    }), 1000)
    return () => clearInterval(timer)
  }, [data])

  const valuesChanged = (_, values) => {
    localStorage.setItem(draftKey, JSON.stringify(values))
    setAnswered(Object.values(values).filter((v) => String(v || '').trim()).length)
  }
  if (!data) return <div className="content-area">正在加载考试并恢复答题记录……</div>
  return <main className="content-area"><Space wrap><Button onClick={() => navigate('/')}>返回</Button><Typography.Title level={3}>{data.exam.title}</Typography.Title><Typography.Text type={left < 300 ? 'danger' : undefined}>剩余 {Math.floor(left / 60)}:{String(left % 60).padStart(2, '0')}</Typography.Text></Space>
    <Progress percent={Math.round(answered / data.questions.length * 100)} />
    <Form form={form} layout="vertical" onFinish={(values) => submitValues(values)} onValuesChange={valuesChanged}>{data.questions.map((q, index) => <Card className="question-card" key={q.question_id}><Typography.Title level={4}>{index + 1}. {q.prompt} <small>{q.phonetic}</small></Typography.Title><Form.Item name={String(q.question_id)} label="请输入中文释义"><Input autoComplete="off" /></Form.Item></Card>)}<Button type="primary" htmlType="submit" size="large" block loading={submitting}>提交试卷</Button></Form>
  </main>
}
