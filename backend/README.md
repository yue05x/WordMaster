# Backend

Flask 后端，包含模块1（用户管理）和模块3（在线考试与自动判卷）。

## 目录结构

```
backend/
├── app.py              # 应用入口
├── config.py           # 配置
├── requirements.txt    # 依赖
├── auth/               # JWT 鉴权
├── models/             # 数据模型
├── routes/             # API 路由
└── services/           # 业务逻辑（判卷、抽题）
```

## 快速启动

```bash
pip install -r requirements.txt
copy .env.example .env
python app.py
```

详细说明见 [docs/module1-module3.md](../docs/module1-module3.md)
