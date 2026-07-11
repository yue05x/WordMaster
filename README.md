# WordMaster

基于英语单词库的在线考试系统。教师可以发布有起止时间的考试；同一场考试的题目集合固定，系统按考生稳定打乱题序；交卷后由后端自动判分，并生成成绩统计和每周错词词云。

## 技术栈

- 前端：React 18、Vite、Ant Design
- 后端：Flask、Flask-SQLAlchemy、JWT
- 数据库：默认 SQLite，可通过 `DATABASE_URL` 切换

## 本地运行

后端：

```powershell
cd backend
python -m pip install -r requirements.txt
python app.py
```

前端（新终端）：

```powershell
cd frontend
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`。教师注册需要邀请码，开发环境默认值为 `teacher123`，可在 `.env` 中通过 `TEACHER_CODE` 修改。

注册和登录都需要选择身份。用户名全系统唯一；教师邀请码错误时注册会被明确拒绝，不会降级为学生账号。

教师端支持单词增删改查、考试发布/编辑/删除、全班成绩与词云；学生端支持答题草稿恢复、到时自动交卷、成绩详情和个人错词词云。

## 核心规则

1. 教师发布考试时随机抽题并持久化，之后不再重新抽取。
2. 每名学生的题序由 `exam_id + user_id` 生成稳定随机顺序，刷新不会变化。
3. 判卷只接受属于该场考试的题目 ID，标准答案只保存在后端。
4. 后端同时校验考试起止时间和个人限时，禁止重复交卷。
5. 词云按最近 7 天的错词次数生成，教师看到全班数据，学生只看到本人数据。

## 分支

- `main`：稳定版本
- `develop`：团队集成版本
- `feature-user`、`feature-word`、`feature-exam`、`feature-statistic`：组员原始模块
