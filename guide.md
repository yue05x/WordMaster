# 成绩统计与字符云模块 — 使用说明与效果说明

> 负责人：姬心慈（成员C）  
> 所属项目：WordMaster 英语单词测试系统  
> 技术栈：Python Flask + SQLAlchemy + MySQL

---

## 一、模块总览

本模块包含4个子模块，共17个RESTful API接口，覆盖成绩统计与字符云展示的全部后端功能。

| 子模块 | 文件夹 | 蓝图前缀 | 接口数 |
|--------|--------|----------|:------:|
| 历史成绩查询 | `history_scores` | `/api/history` | 4 |
| 错题统计 | `wrong_question_stats` | `/api/wrong_stats` | 5 |
| 成绩展示 | `score_display` | `/api/score_display` | 4 |
| 字符云展示 | `wordcloud_display` | `/api/wordcloud` | 4 |

---

## 二、集成方式

在 `app.py` 中导入并初始化四个模块即可：

```python
from flask import Flask
from flask_cors import CORS

from history_scores import init_app as init_history
from wrong_question_stats import init_app as init_wrong_stats
from score_display import init_app as init_score_display
from wordcloud_display import init_app as init_wordcloud

app = Flask(__name__)
CORS(app)

# MySQL 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://用户名:密码@localhost:3306/wordmaster'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 注册四个模块（自动建表 + 注册蓝图）
init_history(app)
init_wrong_stats(app)
init_score_display(app)
init_wordcloud(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**依赖安装**：

```bash
pip install flask flask-cors flask-sqlalchemy pymysql
```

---

## 三、数据库表结构

四个模块共用两张表，`init_app()` 会自动建表。

### exam_record（考试记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 考试记录ID |
| user_id | INT | 用户ID |
| score | FLOAT | 考试得分 |
| total_questions | INT | 题目总数 |
| correct_count | INT | 正确题数 |
| wrong_count | INT | 错误题数 |
| exam_date | DATETIME | 考试时间 |
| duration | INT | 考试用时（秒） |

### answer_record（答题记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 答题记录ID |
| exam_id | INT (FK) | 关联考试记录 |
| word_id | INT | 单词ID |
| word_text | VARCHAR(255) | 单词文本 |
| correct_answer | VARCHAR(255) | 正确答案 |
| user_answer | VARCHAR(255) | 用户答案 |
| is_correct | BOOLEAN | 是否回答正确 |

---

## 四、各模块接口详情

### 4.1 历史成绩查询（`/api/history`）

#### 4.1.1 历史成绩列表

```
GET /api/history/scores?user_id=1&page=1&page_size=10
```

**效果**：按考试时间倒序返回用户的所有考试成绩，支持分页。每页显示10条记录，前端可配合 Ant Design 的 Table 组件实现翻页浏览。

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "records": [
      {
        "id": 5,
        "user_id": 1,
        "score": 85.0,
        "total_questions": 20,
        "correct_count": 17,
        "wrong_count": 3,
        "exam_date": "2026-07-09 14:30:00",
        "duration": 180,
        "accuracy": 85.0
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

---

#### 4.1.2 考试详情

```
GET /api/history/scores/5
```

**效果**：点击某次考试后，展示该次考试的完整详情，包括所有答题记录（每题的正确/错误状态）。

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "exam": { "id": 5, "score": 85.0, "accuracy": 85.0, ... },
    "answers": [
      { "word_text": "apple", "correct_answer": "苹果", "user_answer": "苹果", "is_correct": true },
      { "word_text": "banana", "correct_answer": "香蕉", "user_answer": "香焦", "is_correct": false }
    ]
  }
}
```

---

#### 4.1.3 成绩总览

```
GET /api/history/overview?user_id=1
```

**效果**：返回用户成绩的宏观统计数据，适合在成绩页面顶部展示为统计卡片。

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total_exams": 5,
    "avg_score": 78.4,
    "max_score": 92.0,
    "min_score": 60.0,
    "total_accuracy": 78.0,
    "total_questions_done": 100,
    "total_correct": 78
  }
}
```

---

### 4.2 错题统计（`/api/wrong_stats`）

#### 4.2.1 错题列表

```
GET /api/wrong_stats/list?user_id=1&page=1&page_size=20
```

**效果**：分页展示所有错题，每条包含考试时间、单词、正确答案和用户答案。前端可配合表格展示，方便用户逐条回顾错题。

---

#### 4.2.2 错题汇总

```
GET /api/wrong_stats/summary?user_id=1
```

**效果**：按单词分组统计错题，每个单词显示错误次数、出现总次数、错误率、最近出错时间。适合做"错题排行榜"。

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "summary": [
      {
        "word": "ambiguous",
        "correct_answer": "模棱两可的",
        "wrong_count": 4,
        "total_appear": 5,
        "error_rate": 80.0,
        "last_wrong_date": "2026-07-09 14:30:00"
      }
    ],
    "total_wrong_types": 12,
    "total_wrong_times": 25
  }
}
```

---

#### 4.2.3 错题分布

```
GET /api/wrong_stats/distribution?user_id=1
```

**效果**：按考试分组展示每场考试的错题单词列表，一眼看出哪些考试表现差、哪些单词是"重灾区"。

---

#### 4.2.4 最近错题

```
GET /api/wrong_stats/recent?user_id=1&limit=10
```

**效果**：快速查看最近做错的N道题，适合做成首页的"错题速览"卡片。

---

### 4.3 成绩展示（`/api/score_display`）

#### 4.3.1 考试成绩详情

```
GET /api/score_display/exam/5
```

**效果**：返回单次考试的完整成绩单，正确题和错误题分开列出，每题含正确答案与用户答案对比。前端可做成"成绩单"页面，绿色显示正确题，红色显示错误题。

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "exam": { "id": 5, "score": 85.0, "accuracy": 85.0, ... },
    "correct_list": [
      { "word_text": "apple", "correct_answer": "苹果", "user_answer": "苹果" }
    ],
    "wrong_list": [
      { "word_text": "banana", "correct_answer": "香蕉", "user_answer": "香焦" }
    ],
    "correct_count": 17,
    "wrong_count": 3
  }
}
```

---

#### 4.3.2 成绩趋势

```
GET /api/score_display/trend?user_id=1&limit=10
```

**效果**：返回最近N场考试的分数变化趋势，按时间升序排列。**前端可直接绑定 ECharts / Recharts 折线图**，X轴为考试时间，Y轴为分数。同时返回首末次考试的进步对比数据。

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "trend": [
      { "exam_id": 1, "exam_date": "2026-07-05 10:00:00", "score": 60.0, "accuracy": 60.0 },
      { "exam_id": 2, "exam_date": "2026-07-06 10:00:00", "score": 72.0, "accuracy": 72.0 },
      { "exam_id": 3, "exam_date": "2026-07-07 10:00:00", "score": 85.0, "accuracy": 85.0 }
    ],
    "total_exams": 3,
    "improvement": {
      "first_score": 60.0,
      "last_score": 85.0,
      "change": 25.0,
      "improved": true
    }
  }
}
```

---

#### 4.3.3 成绩总览（统计卡片）

```
GET /api/score_display/overview?user_id=1
```

**效果**：返回成绩统计卡片所需的全量数据，包含：
- 考试总次数、累计答题数
- 平均分、最高分、最低分
- 总正确率
- 最近一次考试详情
- **分数段分布**（0-60 / 60-80 / 80-90 / 90-100），**前端可直接绑定饼图或柱状图**

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total_exams": 5,
    "total_questions": 100,
    "total_correct": 78,
    "avg_score": 78.4,
    "max_score": 92.0,
    "min_score": 60.0,
    "total_accuracy": 78.0,
    "latest_exam": { "id": 5, "score": 85.0, ... },
    "score_distribution": {
      "0-60": 0,
      "60-80": 2,
      "80-90": 2,
      "90-100": 1
    }
  }
}
```

---

#### 4.3.4 成绩对比

```
GET /api/score_display/comparison?user_id=1&exam_ids=1,2,3
```

**效果**：对比多场考试的成绩，不传 `exam_ids` 则默认对比最近3场。**前端可直接绑定柱状图**，每组柱子代表一场考试。

---

### 4.4 字符云展示（`/api/wordcloud`）

#### 4.4.1 错题词云（核心）

```
GET /api/wordcloud/wrong?user_id=1&top_n=50&min_weight=1
```

**效果**：返回错题单词和错误次数，格式为 `[['word', weight], ...]`，**直接兼容 WordCloud2.js**。错误越多的单词权重越大，在词云中字体越大。前端只需一行代码即可渲染：

```javascript
WordCloud(document.getElementById('cloud'), { list: data.wordcloud });
```

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "wordcloud": [
      ["ambiguous", 5],
      ["benevolent", 3],
      ["catastrophe", 3],
      ["diligent", 2]
    ],
    "total_words": 4,
    "weight_range": { "min": 2, "max": 5 },
    "wordcloud_ready": true
  }
}
```

**前端效果预览**：词云中 `ambiguous` 字号最大（错了5次），`diligent` 字号最小（错了2次），直观展示薄弱单词。

---

#### 4.4.2 全部词汇词云

```
GET /api/wordcloud/vocabulary?user_id=1&top_n=50&only_wrong=false
```

**效果**：展示用户所有接触过的单词，权重 = 出现总次数。`only_wrong=true` 时效果等同于错题词云。

---

#### 4.4.3 词云配置建议

```
GET /api/wordcloud/config?user_id=1
```

**效果**：返回 WordCloud2.js 的推荐配置参数（配色方案、字号范围、旋转角度、形状等），前端可直接使用。同时返回数据摘要（总错题数、错题种类数），帮助判断数据是否足够生成有意义的词云。

**返回示例**：

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "suggested_config": {
      "gridSize": 12,
      "sizeRange": [14, 60],
      "rotationRange": [-45, 45],
      "shape": "circle",
      "backgroundColor": "#ffffff",
      "color": "random-dark",
      "weightFactor": 2
    },
    "suggested_colors": [
      "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71",
      "#3498db", "#9b59b6", "#1abc9c", "#34495e"
    ],
    "data_summary": {
      "total_wrong_answers": 25,
      "wrong_word_types": 12,
      "has_enough_data": true
    }
  }
}
```

---

#### 4.4.4 词云单词搜索

```
GET /api/wordcloud/search?user_id=1&keyword=app
```

**效果**：在词云中模糊搜索单词（如搜 `app` 可匹配 `apple`、`application` 等），返回每个匹配单词的正确答案和常见错误答案。

---

## 五、前端联调指南

### 5.1 统一响应格式

所有接口返回 JSON 格式如下：

```json
{
  "code": 200,       // 200=成功, 400=参数错误, 404=记录不存在
  "message": "查询成功",
  "data": { ... }    // 业务数据
}
```

### 5.2 推荐前端组件映射

| 接口 | 推荐前端组件 |
|------|-------------|
| 历史成绩列表 | Ant Design `<Table>` + 分页 |
| 成绩总览统计 | Ant Design `<Card>` + `<Statistic>` |
| 成绩趋势 | ECharts / Recharts 折线图 |
| 分数段分布 | ECharts / Recharts 饼图 |
| 成绩对比 | ECharts / Recharts 柱状图 |
| 错题汇总 | Ant Design `<Table>` + 进度条 |
| 字符云 | WordCloud2.js |

### 5.3 Axios 调用示例

```javascript
import axios from 'axios';

const API_BASE = 'http://localhost:5000';

// 获取历史成绩
axios.get(`${API_BASE}/api/history/scores`, { params: { user_id: 1 } });

// 获取成绩趋势
axios.get(`${API_BASE}/api/score_display/trend`, { params: { user_id: 1 } });

// 获取错题词云数据
axios.get(`${API_BASE}/api/wordcloud/wrong`, { params: { user_id: 1 } });
```

---

## 六、目录结构

```
WM4/
├── PALN.md                    # 项目计划文档
├── guide.md                   # 本文件
├── app.py                     # Flask 主入口（需自行创建）
├── history_scores/            # 历史成绩查询模块
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── wrong_question_stats/      # 错题统计模块
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── score_display/             # 成绩展示模块
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
└── wordcloud_display/         # 字符云展示模块
    ├── __init__.py
    ├── models.py
    └── routes.py
```