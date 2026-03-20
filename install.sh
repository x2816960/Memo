#!/bin/bash

# Memo - 待办任务管理系统 一键安装脚本
# 支持 Ubuntu 18.04/20.04/22.04/24.04

set -e

echo "========================================="
echo "  Memo 安装脚本"
echo "========================================="

# 检测系统版本
detect_ubuntu_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [ "$ID" != "ubuntu" ]; then
            echo "错误: 此脚本仅支持 Ubuntu 系统"
            exit 1
        fi
        VERSION_ID="${VERSION_ID:0:2}"
        echo "检测到 Ubuntu ${VERSION_ID}.04"
        return "$VERSION_ID"
    else
        echo "错误: 无法检测系统版本"
        exit 1
    fi
}

# 安装 Python
install_python() {
    echo "检查 Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        echo "已安装 Python $PYTHON_VERSION"
    else
        echo "安装 Python 3..."
        apt-get update
        apt-get install -y python3 python3-pip python3-venv
    fi
}

# 安装 Node.js
install_nodejs() {
    echo "检查 Node.js..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo "已安装 Node.js $NODE_VERSION"
    else
        echo "安装 Node.js 18..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y nodejs
    fi
}

# 安装后端依赖
install_backend() {
    echo "安装后端依赖..."
    cd "$(dirname "$0")/backend"

    python3 -m venv venv
    source venv/bin/activate

    pip install --upgrade pip
    pip install -r requirements.txt

    echo "后端依赖安装完成"
}

# 安装前端依赖
install_frontend() {
    echo "安装前端依赖..."
    cd "$(dirname "$0")/frontend"

    npm install
    echo "前端依赖安装完成"
}

# 创建必要的目录
create_directories() {
    echo "创建必要的目录..."
    cd "$(dirname "$0")"

    mkdir -p backend/uploads
    mkdir -p backend/logs

    echo "目录创建完成"
}

# 启动服务
start_services() {
    echo "========================================="
    echo "  安装完成!"
    echo "========================================="
    echo ""
    echo "启动后端服务..."
    cd "$(dirname "$0")/backend"
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &
    echo "后端服务已启动 (端口 8000)"

    echo ""
    echo "启动前端服务..."
    cd "$(dirname "$0")/frontend"
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../backend/logs/frontend.log 2>&1 &
    echo "前端服务已启动 (端口 5173)"

    echo ""
    echo "默认管理员账户:"
    echo "  用户名: admin"
    echo "  密码: admin123"
    echo "  (首次登录后请修改密码)"
    echo ""
    echo "访问地址: http://localhost:5173"
}

# 主流程
main() {
    detect_ubuntu_version
    install_python
    install_nodejs
    create_directories
    install_backend
    install_frontend
    start_services
}

main "$@"
