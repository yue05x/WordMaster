import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, Progress, Space, Typography, message } from 'antd'
import { useNavigate, useParams } from 'react-router-dom'
import { examApi } from '../services/api'

export default function Exam() {
  const { examId } = useParams(); const navigate = useNavigate(); const [data, setData] = useState(null); const [left, setLeft] = useState(0); const [form] = Form.useForm()
  useEffect(() => { examApi.start(examId).then((r) => { setData(r.data); setLeft(Math.max(0, Math.floor((new Date(r.data.deadline) - Date.now()) / 1000))) }).catch((e) => { message.error(e.message); navigate('/') }) }, [examId])
  useEffect(() => { if (!data) return; const timer = setInterval(() => setLeft((v) => Math.max(0, v - 1)), 1000); return () => clearInterval(timer) }, [data])
  const submit = async (values) => { try { const answers = data.questions.map((q) => ({ question_id: q.question_id, answer: values[q.question_id] || '' })); const res = await examApi.submit(data.attempt_id, answers); ModalResult(res.data); navigate('/history') } catch (e) { message.error(e.message) } }
  const ModalResult = (result) => message.success(`交卷成功：${result.score} 分，答对 ${result.correct_count}/${result.total_questions} 题`, 5)
  if (!data) return <div className="content-area">正在生成你的题目顺序……</div>
  return <main className="content-area"><Space><Button onClick={() => navigate('/')}>返回</Button><Typography.Title level={3}>{data.exam.title}</Typography.Title><Typography.Text type={left < 300 ? 'danger' : undefined}>剩余 {Math.floor(left / 60)}:{String(left % 60).padStart(2, '0')}</Typography.Text></Space><Progress percent={Math.round((data.questions.filter((q) => form.getFieldValue(q.question_id)).length / data.questions.length) * 100)} />
    <Form form={form} layout="vertical" onFinish={submit}>{data.questions.map((q, i) => <Card className="question-card" key={q.question_id}><Typography.Title level={4}>{i + 1}. {q.prompt} <small>{q.phonetic}</small></Typography.Title><Form.Item name={q.question_id} label="请输入中文释义" rules={[{ required: true, message: '请作答' }]}><Input /></Form.Item></Card>)}<Button type="primary" htmlType="submit" size="large" block disabled={left === 0}>提交试卷</Button></Form>
  </main>
}
