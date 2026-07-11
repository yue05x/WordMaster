import { useEffect, useState } from 'react'
import { Button, Card, Table, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { examApi } from '../services/api'

export default function ExamHistory() {
  const [rows, setRows] = useState([]); const navigate = useNavigate()
  useEffect(() => { examApi.records().then((r) => setRows(r.data)).catch((e) => message.error(e.message)) }, [])
  const columns = [{ title: '考试', dataIndex: 'exam_title' }, { title: '学生', dataIndex: 'student_name' }, { title: '得分', dataIndex: 'score' }, { title: '正确题数', render: (_, r) => `${r.correct_count}/${r.total_questions}` }, { title: '交卷时间', dataIndex: 'end_time', render: (v) => v && new Date(v).toLocaleString() }]
  return <main className="content-area"><Button onClick={() => navigate('/')}>返回首页</Button><Card className="section-card"><Typography.Title level={3}>考试成绩</Typography.Title><Table rowKey="id" dataSource={rows} columns={columns} pagination={{ pageSize: 10 }} /></Card></main>
}
