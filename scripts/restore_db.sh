#!/bin/bash
# 数据库导入脚本 - 从备份恢复 SQLite 数据库

# 配置
DB_PATH="${DB_PATH:-./backend/memo.db}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"

usage() {
    echo "用法: $0 <备份文件路径>"
    echo "示例: $0 ./backups/memo_backup_20260320_143000.db"
    echo ""
    echo "可用备份文件:"
    ls -1 "${BACKUP_DIR}"/memo_backup_*.db 2>/dev/null | sed 's|.*/||'
    exit 1
}

# 检查参数
if [ -z "$1" ]; then
    usage
fi

BACKUP_FILE="$1"

# 检查备份文件是否存在
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "错误: 备份文件不存在: ${BACKUP_FILE}"
    exit 1
fi

# 确认操作
echo "警告: 此操作将用备份文件替换当前数据库!"
echo "当前数据库: ${DB_PATH}"
echo "备份文件:   ${BACKUP_FILE}"
echo ""
read -p "确认继续? (yes/no): " confirm

if [ "${confirm}" != "yes" ]; then
    echo "已取消"
    exit 0
fi

# 停止应用(如果在使用docker-compose)
if docker-compose ps | grep -q "Up"; then
    echo "停止应用..."
    docker-compose stop backend
fi

# 创建当前数据库的临时备份
TEMP_BACKUP="${DB_PATH}.bak.$(date +%s)"
cp "${DB_PATH}" "${TEMP_BACKUP}"
echo "已创建临时备份: ${TEMP_BACKUP}"

# 执行恢复
cp "${BACKUP_FILE}" "${DB_PATH}"

if [ $? -eq 0 ]; then
    echo "恢复成功: ${DB_PATH}"

    # 可选: 恢复上传文件
    UPLOAD_TAR="${BACKUP_FILE%.db}.tar.gz"
    if [ -f "${UPLOAD_TAR}" ]; then
        echo "恢复上传文件..."
        tar -xzf "${UPLOAD_TAR}" -C ./backend
    fi

    # 重新启动应用
    docker-compose start backend
    echo "应用已重新启动"
else
    echo "恢复失败! 从临时备份还原..."
    mv "${TEMP_BACKUP}" "${DB_PATH}"
    exit 1
fi

# 删除临时备份
rm -f "${TEMP_BACKUP}"
