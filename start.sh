#!/bin/bash

# Memo - 启动服务脚本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "  Memo 启动服务"
echo "========================================="
echo ""

# 检查后端依赖
if [ ! -d "$SCRIPT_DIR/backend/venv" ]; then
    echo "错误: 未找到后端虚拟环境，请先运行 install.sh"
    exit 1
fi

# 检查前端依赖
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "错误: 未找到前端依赖，请先运行 install.sh"
    exit 1
fi

# 停止旧服务
echo "停止旧服务..."
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "后端旧服务已停止" || echo "后端旧服务未运行"
pkill -f "vite" 2>/dev/null && echo "前端旧服务已停止" || echo "前端旧服务未运行"
sleep 1

echo ""
echo "启动后端服务..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &
echo "后端服务已启动 (端口 8000)"

echo ""
echo "启动前端服务..."
cd "$SCRIPT_DIR/frontend"
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../backend/logs/frontend.log 2>&1 &
echo "前端服务已启动 (端口 5173)"

echo ""
echo "========================================="
echo "  服务已启动!"
echo "========================================="
echo ""
echo "访问地址: http://localhost:5173"
echo ""
echo "默认管理员账户:"
echo "  用户名: admin"
echo "  密码: admin123"
echo "  (首次登录后请修改密码)"
