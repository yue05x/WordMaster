# 模块1 & 模块3 开发说明

负责人：成员A

## 模块1：用户管理

### 后端接口

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/api/user/register` | 用户注册 | 否 |
| POST | `/api/user/login` | 用户登录 | 否 |
| GET | `/api/user/info` | 获取当前用户信息 | 是 |
| POST | `/api/user/logout` | 退出登录 | 是 |

### 前端页面

- `/login` — 登录页
- `/register` — 注册页

### 鉴权方式

JWT Token，请求头：`Authorization: Bearer <token>`

---

## 模块3：在线考试与自动判卷

### 后端接口

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/api/exam/start` | 开始考试，随机抽题 | 是 |
| POST | `/api/exam/submit` | 提交答卷，自动判卷 | 是 |
| GET | `/api/exam/records` | 历史考试记录 | 是 |
| GET | `/api/exam/<id>` | 单次考试详情 | 是 |

### 前端页面

- `/exam` — 在线答题
- `/exam/result` — 成绩与答题详情
- `/history` — 历史记录列表

### 判卷规则

- 答案忽略首尾空格、大小写
- 支持多释义（分号/逗号分隔），匹配任一即正确

---

## 启动方式

### 1. 初始化数据库

**生产/联调（MySQL）：**

```bash
mysql -u root -p < database/schema.sql
```

在 `backend/.env` 中配置：

```
DATABASE_URL=mysql+pymysql://root:你的密码@localhost:3306/wordmaster?charset=utf8mb4
```

**本地开发（默认 SQLite，无需安装 MySQL）：**

直接启动后端即可，会自动创建 `wordmaster.db` 并导入 20 条示例单词。

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env   # 修改数据库连接
python app.py
```

后端地址：http://localhost:5000

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:5173

---

## 与其他模块的接口约定

### 模块2（成员B）

- 单词表 `word` 已定义，成员B负责导入完整词库
- 抽题逻辑在 `backend/services/exam_service.py`，可替换为模块2的试卷生成算法
- 如需独立试卷生成接口，建议路径：`POST /api/exam/generate`

### 模块4（成员C）

- 可通过 `GET /api/exam/records` 和 `GET /api/exam/<id>` 获取成绩与错题
- 错题数据在 `answer_record` 表中 `is_correct=0` 的记录
