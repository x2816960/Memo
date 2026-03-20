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

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| 认证 | JWT (python-jose + bcrypt) |

## 快速开始

### 方式一: 一键部署 (Ubuntu)

```bash
# 运行安装脚本（首次部署）
chmod +x install.sh
./install.sh

# 启动服务
chmod +x start.sh
./start.sh

# 停止服务
chmod +x stop.sh
./stop.sh
```

访问 http://localhost:5173

**默认管理员账户:**
- 用户名: admin
- 密码: admin123
- (首次登录后请修改密码)

### 方式二: Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
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
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── attachment.py
│   │   │   └── system_config.py
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API 路由
│   │   │   ├── auth.py
│   │   │   ├── tasks.py
│   │   │   ├── attachments.py
│   │   │   └── admin.py
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── uploads/            # 附件存储
│   ├── logs/              # 日志目录
│   ├── venv/              # Python 虚拟环境
│   ├── requirements.txt
│   └── memo.db            # SQLite 数据库
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 调用封装
│   │   ├── components/     # 公共组件
│   │   ├── views/         # 页面组件
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── TaskList.vue
│   │   │   ├── Settings.vue
│   │   │   └── admin/
│   │   ├── router/         # Vue Router 配置
│   │   ├── stores/         # Pinia 状态管理
│   │   └── styles/         # 全局样式
│   ├── node_modules/       # 前端依赖
│   ├── package.json
│   └── vite.config.js
├── docker/                  # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── doc/                    # 文档目录
│   ├── API.md             # API 接口文档
│   ├── 用户指南.md         # 使用手册
│   └── 版本说明.md         # 版本历史
├── install.sh             # 一键安装脚本
├── start.sh              # 启动服务脚本
├── stop.sh               # 停止服务脚本
├── scripts/              # 工具脚本目录
│   ├── backup_db.sh      # 数据库备份脚本
│   └── restore_db.sh    # 数据库恢复脚本
├── docker-compose.yml
└── README.md
```

## 脚本说明

| 脚本 | 说明 |
|------|------|
| install.sh | 首次部署安装脚本，安装依赖、创建目录、启动服务 |
| start.sh | 启动后端和前端服务 |
| stop.sh | 停止所有相关服务 |
| scripts/backup_db.sh | 备份数据库脚本，自动备份到 backpups 目录 |
| scripts/restore_db.sh | 恢复数据库脚本，从备份文件恢复数据库 |

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 5173 | Vue 开发服务器 |
| 后端 | 8000 | FastAPI 服务 |
| Nginx | 80 | Docker 部署时使用 |

## 常见问题

**Q: 安装失败怎么办？**
A: 确保已安装 Python 3.8+ 和 Node.js 18+。详细日志查看 `backend/logs/app.log`。

**Q: 端口被占用怎么办？**
A: 运行 `./stop.sh` 停止服务，或手动 `pkill -f uvicorn` / `pkill -f vite`。

**Q: 如何重置管理员密码？**
A: 删除 `backend/memo.db` 后重新运行 `./start.sh`，会重新创建管理员账户。

## API 接口

详见 [API.md](./doc/API.md)

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

### 附件接口
- `POST /api/tasks/:id/attachments` - 上传附件
- `GET /api/tasks/:id/attachments` - 获取附件列表
- `GET /api/attachments/:id/download` - 下载附件
- `DELETE /api/attachments/:id` - 删除附件

### 管理员接口
- `GET /api/admin/users` - 用户列表
- `PATCH /api/admin/users/:id` - 启用/禁用用户
- `POST /api/admin/users/:id/reset-password` - 重置密码
- `GET /api/admin/stats` - 系统统计
- `GET /api/admin/config` - 获取配置
- `PUT /api/admin/config` - 更新配置

## License

MIT
