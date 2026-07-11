import { useEffect, useState } from 'react'
import { Button, Card, Col, DatePicker, Form, Input, InputNumber, Layout, Modal, Popconfirm, Row, Space, Statistic, Tag, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { examApi, statisticApi, userApi } from '../services/api'

const statusText = { running: '进行中', upcoming: '未开始', finished: '已结束', draft: '草稿' }
export default function Home() {
  const [exams, setExams] = useState([])
  const [overview, setOverview] = useState({})
  const [words, setWords] = useState([])
  const [editing, setEditing] = useState(null)
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const load = async () => { try { const [e, s, w] = await Promise.all([examApi.list(), statisticApi.overview(), statisticApi.wordcloud()]); setExams(e.data); setOverview(s.data); setWords(w.data) } catch (e) { message.error(e.message) } }
  useEffect(() => { load() }, [])
  const showExamForm = (exam = null) => {
    setEditing(exam)
    form.setFieldsValue(exam ? { title: exam.title, description: exam.description, time: [dayjs(exam.start_time), dayjs(exam.end_time)], duration_minutes: exam.duration_minutes } : { question_count: 10, duration_minutes: 30 })
    setOpen(true)
  }
  const saveExam = async (values) => {
    const windowMinutes = values.time[1].diff(values.time[0], 'minute', true)
    if (windowMinutes < values.duration_minutes) {
      message.error(`考试开放时间不能少于个人限时 ${values.duration_minutes} 分钟`)
      return
    }
    const payload = { ...values, start_time: values.time[0].toISOString(), end_time: values.time[1].toISOString() }
    delete payload.time
    try { editing ? await examApi.update(editing.id, payload) : await examApi.create(payload); message.success(editing ? '考试修改成功' : '考试发布成功'); setOpen(false); form.resetFields(); load() } catch (e) { message.error(e.message) }
  }
  const removeExam = async (id) => { try { await examApi.remove(id); message.success('考试删除成功'); load() } catch (e) { message.error(e.message) } }
  const signOut = async () => { try { await userApi.logout() } catch {} logout(); navigate('/login') }
  return <Layout className="main-layout"><header className="topbar"><Typography.Title level={3}>WordMaster</Typography.Title><Space wrap><span>{user?.nickname}（{user?.role === 'teacher' ? '教师' : '学生'}）</span>{user?.role === 'teacher' && <Button onClick={() => navigate('/words')}>单词库管理</Button>}<Button onClick={() => navigate('/history')}>成绩记录</Button><Button onClick={signOut}>退出</Button></Space></header>
    <main className="content-area"><Row gutter={[16, 16]}><Col xs={24} md={8}><Card><Statistic title={user?.role === 'teacher' ? '全班交卷次数' : '我的考试次数'} value={overview.exam_count || 0} /></Card></Col><Col xs={24} md={8}><Card><Statistic title="平均分" value={overview.average_score || 0} /></Card></Col><Col xs={24} md={8}><Card><Statistic title="最高分" value={overview.highest_score || 0} /></Card></Col></Row>
    <Card title={user?.role === 'teacher' ? '本周全班薄弱单词词云' : '本周我的薄弱单词词云'} className="section-card"><div className="word-cloud">{words.length ? words.map((w) => <span key={w.word} title={`${w.meaning} · 错误 ${w.weight} 次`} style={{ fontSize: 15 + Math.min(w.weight, 8) * 5 }}>{w.word}</span>) : <Typography.Text type="secondary">完成考试并产生错题后，这里会动态生成词云。</Typography.Text>}</div></Card>
    <Card title="考试列表" className="section-card" extra={user?.role === 'teacher' && <Button type="primary" onClick={() => showExamForm()}>发布考试</Button>}>
      {!exams.length && <Typography.Text type="secondary">目前还没有考试。{user?.role === 'teacher' ? '请点击右上角发布考试。' : '请等待教师发布。'}</Typography.Text>}
      <Row gutter={[16, 16]}>{exams.map((exam) => <Col xs={24} md={12} key={exam.id}><Card size="small" title={exam.title} extra={<Tag color={exam.status === 'running' ? 'green' : 'default'}>{statusText[exam.status]}</Tag>}><p>{exam.question_count} 题 · {exam.duration_minutes} 分钟</p><p>{new Date(exam.start_time).toLocaleString()} 至 {new Date(exam.end_time).toLocaleString()}</p>{user?.role === 'student' ? <Button type="primary" disabled={exam.status !== 'running'} onClick={() => navigate(`/exam/${exam.id}`)}>进入考试</Button> : <Space><Button disabled={exam.status === 'finished'} onClick={() => showExamForm(exam)}>编辑</Button><Popconfirm title="确认删除这场考试？" onConfirm={() => removeExam(exam.id)}><Button danger>删除</Button></Popconfirm></Space>}</Card></Col>)}</Row>
    </Card></main>
    <Modal title={editing ? '编辑考试' : '发布考试'} open={open} onCancel={() => setOpen(false)} footer={null}><Form form={form} layout="vertical" onFinish={saveExam}><Form.Item label="考试名称" name="title" rules={[{ required: true }]}><Input /></Form.Item><Form.Item label="考试说明" name="description"><Input.TextArea /></Form.Item><Form.Item label="起止时间（开放窗口应不少于考试限时）" name="time" rules={[{ required: true }]}><DatePicker.RangePicker showTime={{ format: 'HH:mm' }} format="YYYY-MM-DD HH:mm" /></Form.Item>{!editing && <Form.Item label="题目数量" name="question_count" rules={[{ required: true }]}><InputNumber min={1} max={100} /></Form.Item>}<Form.Item label="个人考试限时（分钟）" name="duration_minutes" rules={[{ required: true }]}><InputNumber min={1} /></Form.Item><Button type="primary" htmlType="submit" block>{editing ? '保存修改' : '发布并固定题目'}</Button></Form></Modal>
  </Layout>
}
