import { useEffect, useState } from 'react'
import { Button, Card, Col, DatePicker, Form, Input, InputNumber, Layout, Modal, Row, Space, Statistic, Tag, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { examApi, statisticApi, userApi } from '../services/api'

const statusText = { running: '进行中', upcoming: '未开始', finished: '已结束', draft: '草稿' }
export default function Home() {
  const [exams, setExams] = useState([]); const [overview, setOverview] = useState({}); const [words, setWords] = useState([])
  const [open, setOpen] = useState(false); const [form] = Form.useForm(); const { user, logout } = useAuth(); const navigate = useNavigate()
  const load = async () => { try { const [e, s, w] = await Promise.all([examApi.list(), statisticApi.overview(), statisticApi.wordcloud()]); setExams(e.data); setOverview(s.data); setWords(w.data) } catch (e) { message.error(e.message) } }
  useEffect(() => { load() }, [])
  const createExam = async (v) => { try { await examApi.create({ ...v, start_time: v.time[0].toISOString(), end_time: v.time[1].toISOString() }); message.success('考试发布成功'); setOpen(false); form.resetFields(); load() } catch (e) { message.error(e.message) } }
  const signOut = async () => { try { await userApi.logout() } catch {} logout(); navigate('/login') }
  return <Layout className="main-layout"><header className="topbar"><Typography.Title level={3}>WordMaster</Typography.Title><Space><span>{user?.nickname}（{user?.role === 'teacher' ? '教师' : '学生'}）</span><Button onClick={() => navigate('/history')}>成绩记录</Button><Button onClick={signOut}>退出</Button></Space></header>
    <main className="content-area"><Row gutter={[16, 16]}><Col span={8}><Card><Statistic title="考试次数" value={overview.exam_count || 0} /></Card></Col><Col span={8}><Card><Statistic title="平均分" value={overview.average_score || 0} /></Card></Col><Col span={8}><Card><Statistic title="最高分" value={overview.highest_score || 0} /></Card></Col></Row>
    <Card title="本周薄弱单词词云" className="section-card"><div className="word-cloud">{words.length ? words.map((w) => <span key={w.word} title={w.meaning} style={{ fontSize: 15 + Math.min(w.weight, 8) * 5 }}>{w.word}</span>) : <Typography.Text type="secondary">完成考试后，这里会根据错题动态生成词云。</Typography.Text>}</div></Card>
    <Card title="考试列表" className="section-card" extra={user?.role === 'teacher' && <Button type="primary" onClick={() => setOpen(true)}>发布考试</Button>}>
      <Row gutter={[16, 16]}>{exams.map((exam) => <Col xs={24} md={12} key={exam.id}><Card size="small" title={exam.title} extra={<Tag color={exam.status === 'running' ? 'green' : 'default'}>{statusText[exam.status]}</Tag>}><p>{exam.question_count} 题 · {exam.duration_minutes} 分钟</p><p>{new Date(exam.start_time).toLocaleString()} 至 {new Date(exam.end_time).toLocaleString()}</p>{user?.role === 'student' && <Button type="primary" disabled={exam.status !== 'running'} onClick={() => navigate(`/exam/${exam.id}`)}>进入考试</Button>}</Card></Col>)}</Row>
    </Card></main>
    <Modal title="发布考试" open={open} onCancel={() => setOpen(false)} footer={null}><Form form={form} layout="vertical" onFinish={createExam}><Form.Item label="考试名称" name="title" rules={[{ required: true }]}><Input /></Form.Item><Form.Item label="起止时间" name="time" rules={[{ required: true }]}><DatePicker.RangePicker showTime /></Form.Item><Form.Item label="题目数量" name="question_count" initialValue={10}><InputNumber min={1} max={100} /></Form.Item><Form.Item label="限时（分钟）" name="duration_minutes" initialValue={30}><InputNumber min={1} /></Form.Item><Button type="primary" htmlType="submit" block>发布并固定题目</Button></Form></Modal>
  </Layout>
}
