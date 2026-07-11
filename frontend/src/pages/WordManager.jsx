import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, Modal, Popconfirm, Space, Table, Typography, message } from 'antd'
import { useNavigate } from 'react-router-dom'
import { wordApi } from '../services/api'

export default function WordManager() {
  const [rows, setRows] = useState([])
  const [editing, setEditing] = useState(null)
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const load = async (q = query) => { try { setRows((await wordApi.list(q)).data) } catch (e) { message.error(e.message) } }
  useEffect(() => { load('') }, [])
  const showForm = (record = null) => { setEditing(record); form.setFieldsValue(record || { level: 'CET4' }); setOpen(true) }
  const save = async (values) => { try { editing ? await wordApi.update(editing.id, values) : await wordApi.create(values); message.success(editing ? '修改成功' : '添加成功'); setOpen(false); form.resetFields(); load() } catch (e) { message.error(e.message) } }
  const remove = async (id) => { try { await wordApi.remove(id); message.success('删除成功'); load() } catch (e) { message.error(e.message) } }
  const columns = [
    { title: '单词', dataIndex: 'word' }, { title: '中文释义', dataIndex: 'meaning' },
    { title: '音标', dataIndex: 'phonetic' }, { title: '等级', dataIndex: 'level' },
    { title: '操作', render: (_, row) => <Space><Button size="small" onClick={() => showForm(row)}>编辑</Button><Popconfirm title="确认删除？" onConfirm={() => remove(row.id)}><Button size="small" danger>删除</Button></Popconfirm></Space> },
  ]
  return <main className="content-area"><Space><Button onClick={() => navigate('/')}>返回首页</Button><Typography.Title level={3}>单词库管理</Typography.Title></Space>
    <Card><Space className="toolbar"><Input.Search placeholder="搜索英文单词" allowClear onSearch={(v) => { setQuery(v); load(v) }} /><Button type="primary" onClick={() => showForm()}>添加单词</Button></Space><Table rowKey="id" dataSource={rows} columns={columns} /></Card>
    <Modal title={editing ? '编辑单词' : '添加单词'} open={open} onCancel={() => setOpen(false)} footer={null}><Form form={form} layout="vertical" onFinish={save}><Form.Item label="英文单词" name="word" rules={[{ required: true }]}><Input /></Form.Item><Form.Item label="中文释义" name="meaning" rules={[{ required: true }]}><Input /></Form.Item><Form.Item label="音标" name="phonetic"><Input /></Form.Item><Form.Item label="等级" name="level"><Input /></Form.Item><Button htmlType="submit" type="primary" block>保存</Button></Form></Modal>
  </main>
}
