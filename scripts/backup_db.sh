#!/bin/bash
# 数据库导出脚本 - 备份 SQLite 数据库

# 配置
DB_PATH="${DB_PATH:-./backend/memo.db}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/memo_backup_${TIMESTAMP}.db"

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

# 检查数据库文件是否存在
if [ ! -f "${DB_PATH}" ]; then
    echo "错误: 数据库文件不存在: ${DB_PATH}"
    exit 1
fi

# 执行备份
cp "${DB_PATH}" "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "备份成功: ${BACKUP_FILE}"

    # 可选: 同时备份上传的文件
    if [ -d "./backend/uploads" ]; then
        UPLOAD_BACKUP="${BACKUP_DIR}/uploads_${TIMESTAMP}.tar.gz"
        tar -czf "${UPLOAD_BACKUP}" -C ./backend uploads 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "上传文件备份: ${UPLOAD_BACKUP}"
        fi
    fi

    # 清理旧备份（保留最近10个）
    cd "${BACKUP_DIR}" && ls -t memo_backup_*.db | tail -n +11 | xargs -r rm
    echo "旧备份已清理，保留最近10个备份"
else
    echo "备份失败!"
    exit 1
fi
