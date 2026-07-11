import { useEffect, useMemo, useState } from 'react'
import { Button, Card, Col, DatePicker, Empty, Form, Input, InputNumber, Layout, List, Modal, Popconfirm, Progress, Row, Segmented, Space, Statistic, Tag, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { examApi, statisticApi, userApi } from '../services/api'

const statusText = { running: '进行中', upcoming: '未开始', finished: '已结束', draft: '草稿' }
const statusColor = { running: 'green', upcoming: 'blue', finished: 'default', draft: 'orange' }

export default function Home() {
  const [exams, setExams] = useState([])
  const [overview, setOverview] = useState({})
  const [words, setWords] = useState([])
  const [trend, setTrend] = useState([])
  const [leaderboard, setLeaderboard] = useState([])
  const [filter, setFilter] = useState('全部')
  const [editing, setEditing] = useState(null)
  const [selectedWord, setSelectedWord] = useState(null)
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const load = async () => {
    try {
      const [e, s, w, t, l] = await Promise.all([
        examApi.list(), statisticApi.overview(), statisticApi.wordcloud(30),
        statisticApi.trend(), statisticApi.leaderboard(),
      ])
      setExams(e.data); setOverview(s.data); setWords(w.data); setTrend(t.data); setLeaderboard(l.data)
    } catch (error) { message.error(error.message) }
  }
  useEffect(() => { load() }, [])

  const filteredExams = useMemo(() => exams.filter((exam) => {
    if (filter === '全部') return true
    return statusText[exam.status] === filter
  }), [exams, filter])

  const showExamForm = (exam = null) => {
    setEditing(exam)
    form.setFieldsValue(exam ? {
      title: exam.title, description: exam.description,
      time: [dayjs(exam.start_time), dayjs(exam.end_time)], duration_minutes: exam.duration_minutes,
    } : { question_count: 10, duration_minutes: 30 })
    setOpen(true)
  }
  const saveExam = async (values) => {
    const windowMinutes = values.time[1].diff(values.time[0], 'minute', true)
    if (windowMinutes < values.duration_minutes) {
      message.error(`考试开放时间不能少于个人限时 ${values.duration_minutes} 分钟`); return
    }
    const payload = { ...values, start_time: values.time[0].toISOString(), end_time: values.time[1].toISOString() }
    delete payload.time
    try {
      editing ? await examApi.update(editing.id, payload) : await examApi.create(payload)
      message.success(editing ? '考试修改成功' : '考试发布成功')
      setOpen(false); form.resetFields(); load()
    } catch (error) { message.error(error.message) }
  }
  const removeExam = async (id) => { try { await examApi.remove(id); message.success('考试删除成功'); load() } catch (e) { message.error(e.message) } }
  const signOut = async () => { try { await userApi.logout() } catch {} logout(); navigate('/login') }

  const runningCount = exams.filter((exam) => exam.status === 'running').length
  const greeting = new Date().getHours() < 12 ? '早上好' : new Date().getHours() < 18 ? '下午好' : '晚上好'

  return <Layout className="main-layout">
    <header className="topbar"><div className="brand"><span className="brand-mark">W</span><div><Typography.Title level={3}>WordMaster</Typography.Title><small>英语词汇学习与考试系统</small></div></div><Space wrap><span>{user?.nickname}（{user?.role === 'teacher' ? '教师' : '学生'}）</span>{user?.role === 'teacher' && <Button onClick={() => navigate('/words')}>单词库管理</Button>}<Button onClick={() => navigate('/history')}>成绩记录</Button><Button onClick={signOut}>退出</Button></Space></header>
    <main className="content-area">
      <section className="page-heading"><div className="heading-copy"><span className="today-label">今日学习台</span><Typography.Title level={2}>{greeting}，{user?.nickname || user?.username} 👋</Typography.Title><Typography.Paragraph>{user?.role === 'teacher' ? '来看看班级最近的学习进展和考试安排吧。' : '今天也积累一点点，单词会慢慢变成你的长期记忆。'}</Typography.Paragraph><Space><Button type="primary" onClick={() => user?.role === 'teacher' ? showExamForm() : document.getElementById('exam-list')?.scrollIntoView({ behavior: 'smooth' })}>{user?.role === 'teacher' ? '发布考试' : '查看考试'}</Button><Button onClick={() => navigate('/history')}>查看成绩</Button></Space></div><div className="heading-note"><span>📚</span><strong>{runningCount ? `${runningCount} 场考试进行中` : '暂无进行中考试'}</strong><small>{user?.role === 'teacher' ? '记得关注学生完成情况' : '合理安排今天的复习时间'}</small></div></section>

      <Row gutter={[16, 16]} className="metric-grid">
        <Col xs={12} lg={6}><Card className="metric-card metric-navy"><span className="metric-emoji">📝</span><Statistic title={user?.role === 'teacher' ? '全班交卷次数' : '我的考试次数'} value={overview.exam_count || 0} /></Card></Col>
        <Col xs={12} lg={6}><Card className="metric-card metric-blue"><span className="metric-emoji">📊</span><Statistic title="平均成绩" value={overview.average_score || 0} suffix="分" /></Card></Col>
        <Col xs={12} lg={6}><Card className="metric-card metric-green"><span className="metric-emoji">🏅</span><Statistic title="历史最高" value={overview.highest_score || 0} suffix="分" /></Card></Col>
        <Col xs={12} lg={6}><Card className="metric-card metric-gold"><span className="metric-emoji">⏳</span><Statistic title="进行中考试" value={runningCount} /></Card></Col>
      </Row>

      <Row gutter={[20, 20]} className="dashboard-row">
        <Col xs={24} lg={15}><Card title="📈 近期成绩趋势" extra={<span className="card-note">最近 {trend.length} 次记录</span>} className="data-card trend-card"><div className="trend-chart">{trend.length ? trend.map((item) => <div className="trend-item" key={item.id} title={`${item.exam} · ${item.score}分`}><span className="trend-value">{item.score}</span><div className="trend-track"><i style={{ height: `${Math.max(item.score, 8)}%` }} /></div><small>{new Date(item.date).getMonth() + 1}/{new Date(item.date).getDate()}</small></div>) : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="完成考试后生成趋势" />}</div></Card></Col>
        <Col xs={24} lg={9}><Card title="🏆 学习成绩排行" extra={<span className="card-note">按平均分排序</span>} className="data-card leaderboard rank-card"><List dataSource={leaderboard.slice(0, 5)} locale={{ emptyText: '暂无排行数据' }} renderItem={(item) => <List.Item><List.Item.Meta avatar={<span className={`rank rank-${item.rank}`}>{item.rank}</span>} title={item.student} description={`${item.exam_count} 次考试，最高 ${item.highest_score} 分`} /><strong>{item.average_score}</strong></List.Item>} /></Card></Col>
      </Row>

      <Card title={`🌱 ${user?.role === 'teacher' ? '班级薄弱词汇' : '我的薄弱词汇'}`} extra={<span className="card-note">统计周期：近 30 天</span>} className="section-card data-card word-card"><div className="word-cloud rich-cloud">{words.length ? words.map((word) => <button type="button" key={word.word} onClick={() => setSelectedWord(word)} title={`${word.meaning} · 错误 ${word.weight} 次`} style={{ fontSize: 15 + Math.min(word.weight, 8) * 4 }}>{word.word}</button>) : <Typography.Text type="secondary">完成考试并产生错题后，这里会显示需要重点复习的词汇。</Typography.Text>}</div></Card>

      <Card id="exam-list" title="📅 考试安排" className="section-card data-card exam-section" extra={user?.role === 'teacher' && <Button type="primary" onClick={() => showExamForm()}>发布考试</Button>}><Segmented value={filter} onChange={setFilter} options={['全部', '进行中', '未开始', '已结束']} className="exam-filter" />
        {!filteredExams.length && <Empty description="当前筛选条件下没有考试" />}
        <Row gutter={[16, 16]}>{filteredExams.map((exam) => <Col xs={24} md={12} xl={8} key={exam.id}><Card className="exam-card" title={exam.title} extra={<Tag color={statusColor[exam.status]}>{statusText[exam.status]}</Tag>}><Typography.Paragraph type="secondary">{exam.description || '英语词汇能力专项检测'}</Typography.Paragraph><div className="exam-meta"><span>{exam.question_count} 题</span><span>{exam.duration_minutes} 分钟</span></div><p className="exam-time">开始：{new Date(exam.start_time).toLocaleString()}<br />结束：{new Date(exam.end_time).toLocaleString()}</p>{user?.role === 'student' ? <Button type="primary" block disabled={exam.status !== 'running'} onClick={() => navigate(`/exam/${exam.id}`)}>{exam.status === 'running' ? '进入考试' : statusText[exam.status]}</Button> : <Space><Button disabled={exam.status === 'finished'} onClick={() => showExamForm(exam)}>编辑</Button><Popconfirm title="确认删除这场考试？" onConfirm={() => removeExam(exam.id)}><Button danger>删除</Button></Popconfirm></Space>}</Card></Col>)}</Row>
      </Card>
    </main>

    <Modal title={selectedWord?.word} open={!!selectedWord} onCancel={() => setSelectedWord(null)} footer={<Button onClick={() => setSelectedWord(null)}>知道了</Button>}><Typography.Title level={4}>可接受释义</Typography.Title><div className="meaning-tags">{selectedWord?.meaning.split('；').map((item) => <Tag color="blue" key={item}>{item}</Tag>)}</div><Typography.Paragraph className="review-tip">近 30 天错误 {selectedWord?.weight} 次。建议抄写、朗读并尝试造句，加深记忆。</Typography.Paragraph><Progress percent={Math.max(10, 100 - (selectedWord?.weight || 0) * 12)} status="active" /></Modal>
    <Modal title={editing ? '编辑考试' : '发布考试'} open={open} onCancel={() => setOpen(false)} footer={null}><Form form={form} layout="vertical" onFinish={saveExam}><Form.Item label="考试名称" name="title" rules={[{ required: true }]}><Input /></Form.Item><Form.Item label="考试说明" name="description"><Input.TextArea /></Form.Item><Form.Item label="起止时间（开放窗口应不少于考试限时）" name="time" rules={[{ required: true }]}><DatePicker.RangePicker showTime={{ format: 'HH:mm' }} format="YYYY-MM-DD HH:mm" /></Form.Item>{!editing && <Form.Item label="题目数量" name="question_count" rules={[{ required: true }]}><InputNumber min={1} max={100} /></Form.Item>}<Form.Item label="个人考试限时（分钟）" name="duration_minutes" rules={[{ required: true }]}><InputNumber min={1} /></Form.Item><Button type="primary" htmlType="submit" block>{editing ? '保存修改' : '发布并固定题目'}</Button></Form></Modal>
  </Layout>
}
