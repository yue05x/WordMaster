# WordMaster

WordMaster 是一个基于离线英语单词库的在线学习与考试系统。教师可以维护词库、发布限时考试并查看班级学习数据；学生可以参加考试、自动判卷、查看成绩详情并根据薄弱词汇进行复习。

## 主要功能

### 教师端

- 教师邀请码注册及身份校验；
- 单词查询、新增、编辑和安全删除；
- 发布、编辑和删除考试；
- 设置考试起止时间、题目数量和个人限时；
- 查看全班成绩、答题详情、成绩趋势和排行榜；
- 查看近 30 天班级薄弱词汇。

### 学生端

- 查看考试状态并在开放时间内参加考试；
- 同场考试题目一致，题序按学生稳定打乱；
- 答题草稿自动保存，刷新页面后恢复；
- 倒计时结束自动交卷，后端自动判分；
- 查看个人成绩、每题正误和正确答案；
- 查看成绩趋势、排行榜及个人薄弱词汇。

### 单词与判卷

- 内置 126 个常用英语单词；
- 一个单词可以配置多个中文释义，使用分号分隔；
- 判卷接受词库中登记的任意一个释义；
- 离线运行，不依赖第三方词典密钥、网络或调用额度；
- 词库更新后可以重新核验已有答题记录。

## 技术栈

- 前端：React 18、Vite、Ant Design、Axios
- 后端：Flask、Flask-SQLAlchemy、JWT、bcrypt
- 数据库：默认 SQLite，可通过 `DATABASE_URL` 切换为其他数据库

## 项目结构

```text
WordMaster/
├─ backend/              Flask 后端、模型、接口、脚本和测试
├─ frontend/             React 前端
├─ database/schema.sql   MySQL 参考建表脚本
├─ docs/                 项目文档
├─ guide.md              功能与演示指南
└─ README.md
```

## 本地运行

### 1. 启动后端

```powershell
cd C:\Users\Administrator\Desktop\WordMaster\backend
python -m pip install -r requirements.txt
python app.py
```

后端默认地址：`http://127.0.0.1:5000`。

### 2. 启动前端

打开新的 PowerShell：

```powershell
cd C:\Users\Administrator\Desktop\WordMaster\frontend
npm.cmd install
npm.cmd run dev
```

浏览器访问：`http://localhost:5173`。

## 身份规则

- 注册和登录时都必须选择学生或教师身份；
- 用户名全系统唯一；
- 教师注册需要邀请码，开发环境默认值为 `teacher123`；
- 可在 `backend/.env` 中使用 `TEACHER_CODE` 修改邀请码；
- 教师邀请码错误时注册会被拒绝，不会自动降级为学生。

## 演示数据

需要丰富的演示内容时运行：

```powershell
python backend\scripts\seed_demo.py
```

该脚本可以重复运行，不会重复创建相同演示记录。演示账号密码均为 `123456`：

| 身份 | 用户名 | 昵称 |
|---|---|---|
| 教师 | `demo_teacher` | 张老师 |
| 学生 | `demo_alice` | 林晓雨 |
| 学生 | `demo_bob` | 陈子轩 |
| 学生 | `demo_carol` | 周思涵 |
| 学生 | `demo_david` | 王浩然 |

## 测试与构建

后端自动化测试：

```powershell
python -m unittest discover -s backend/tests -v
```

前端生产构建：

```powershell
cd frontend
npm.cmd run build
```

## 核心业务规则

1. 教师发布考试时抽取并持久化题目，之后不会为每名学生重新抽题。
2. 每名学生的题序由考试 ID 和用户 ID 生成稳定随机顺序。
3. 标准答案保存在后端，交卷时校验题目是否属于当前考试。
4. 后端同时检查考试开放窗口和个人考试限时。
5. 考试开放窗口不能短于个人考试限时。
6. 同一名学生不能重复提交同一场考试。
7. 学生只能查看个人数据，教师可以查看班级汇总数据。

## Git 分支

- `main`：最终稳定版本
- `develop`：团队集成与开发版本
- `feature-user`、`feature-word`、`feature-exam`、`feature-statistic`：组员原始功能分支

更完整的演示流程请查看 [guide.md](guide.md)。
