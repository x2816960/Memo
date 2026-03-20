#!/bin/bash

# Memo - 停止服务脚本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "  Memo 停止服务"
echo "========================================="

# 停止后端服务
echo "停止后端服务..."
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "后端服务已停止" || echo "后端服务未运行"

# 停止前端服务
echo "停止前端服务..."
pkill -f "vite" 2>/dev/null && echo "前端服务已停止" || echo "前端服务未运行"

# 清理端口占用（确保端口释放）
echo "释放端口..."
fuser -k 8000/tcp 2>/dev/null && echo "端口 8000 已释放" || echo "端口 8000 未被占用"
fuser -k 5173/tcp 2>/dev/null && echo "端口 5173 已释放" || echo "端口 5173 未被占用"

echo ""
echo "所有服务已停止"
