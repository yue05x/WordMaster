import { useEffect, useState } from 'react'
import { Button, Card, Drawer, Table, Tag, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { examApi } from '../services/api'

export default function ExamHistory() {
  const [rows, setRows] = useState([])
  const [detail, setDetail] = useState(null)
  const navigate = useNavigate()
  useEffect(() => { examApi.records().then((res) => setRows(res.data)).catch((e) => message.error(e.message)) }, [])
  const showDetail = async (id) => { try { setDetail((await examApi.detail(id)).data) } catch (e) { message.error(e.message) } }
  const columns = [
    { title: '考试', dataIndex: 'exam_title' }, { title: '学生', dataIndex: 'student_name' },
    { title: '得分', dataIndex: 'score', render: (v) => <strong>{v}</strong> },
    { title: '正确题数', render: (_, r) => `${r.correct_count}/${r.total_questions}` },
    { title: '交卷时间', dataIndex: 'end_time', render: (v) => v && new Date(v).toLocaleString() },
    { title: '操作', render: (_, r) => <Button size="small" onClick={() => showDetail(r.id)}>查看答题详情</Button> },
  ]
  const answerColumns = [
    { title: '题号', dataIndex: 'question_order', width: 70 }, { title: '单词', dataIndex: 'word' },
    { title: '我的答案', dataIndex: 'user_answer' }, { title: '正确答案', dataIndex: 'correct_answer' },
    { title: '结果', dataIndex: 'is_correct', render: (v) => <Tag color={v ? 'green' : 'red'}>{v ? '正确' : '错误'}</Tag> },
  ]
  return <main className="content-area"><Button onClick={() => navigate('/')}>返回首页</Button><Card className="section-card"><Typography.Title level={3}>考试成绩</Typography.Title><Table rowKey="id" dataSource={rows} columns={columns} pagination={{ pageSize: 10 }} /></Card>
    <Drawer title={detail ? `${detail.exam_title} · ${detail.score} 分` : '答题详情'} width={760} open={!!detail} onClose={() => setDetail(null)}><Table rowKey="id" pagination={false} dataSource={detail?.answers || []} columns={answerColumns} /></Drawer>
  </main>
}
