# Memo - 待办任务管理系统

一个基于 Web 的多用户待办任务管理系统。

## 功能特性

- 用户注册/登录 (JWT 认证)
- 任务 CRUD (创建/编辑/删除/列表)
- 任务状态流转 (待办 → 进行中 → 已完成/已取消)
- 任务筛选和搜索
- 拖拽排序
- 附件上传
- 任务统计面板
- 管理员功能 (用户管理、系统配置、系统统计)

## 技术栈

- 前端: Vue 3 + Element Plus + Vite
- 后端: Python FastAPI + SQLAlchemy
- 数据库: SQLite
- 认证: JWT

## 快速开始

### 方式一: 直接部署 (Ubuntu)

```bash
# 克隆项目后运行安装脚本
chmod +x install.sh
./install.sh
```

访问 http://localhost:5173

默认管理员账户:
- 用户名: admin
- 密码: admin123

### 方式二: Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问 http://localhost

### 方式三: 开发模式

```bash
# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 项目结构

```
memo/
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── database.py     # 数据库配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   └── requirements.txt
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 调用
│   │   ├── components/     # 公共组件
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   └── stores/         # 状态管理
│   └── package.json
├── docker/                  # Docker 配置
├── install.sh              # 一键安装脚本
└── docker-compose.yml      # Docker Compose 配置
```

## API 接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 退出登录
- `GET /api/auth/me` - 获取当前用户
- `PUT /api/auth/password` - 修改密码

### 任务接口
- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建任务
- `PUT /api/tasks/:id` - 更新任务
- `DELETE /api/tasks/:id` - 删除任务
- `PATCH /api/tasks/:id/status` - 更新状态
- `PUT /api/tasks/sort` - 保存排序
- `GET /api/tasks/stats` - 获取统计

### 管理员接口
- `GET /api/admin/users` - 用户列表
- `PATCH /api/admin/users/:id` - 启用/禁用用户
- `POST /api/admin/users/:id/reset-password` - 重置密码
- `GET /api/admin/stats` - 系统统计
- `GET /api/admin/config` - 获取配置
- `PUT /api/admin/config` - 更新配置

## License

MIT
