# Memo API 接口文档

> 版本: v1.0.0
> 日期: 2026-03-20

---

## 概述

Memo API 是一个基于 RESTful 风格的 Web API，采用 JWT Token 进行身份认证。

**基础 URL**: `http://{host}:{port}/api`

**认证方式**: Bearer Token (JWT)

**请求格式**: `Content-Type: application/json`

**响应格式**:
```json
{
  "data": { ... },
  "message": "success"
}
```

**错误响应**:
```json
{
  "detail": "错误描述"
}
```

---

## 认证接口

### 1. 用户注册

**POST** `/api/auth/register`

注册新用户账户。

**请求体**:
```json
{
  "username": "string (必填, 4-20位, 字母/数字/下划线)",
  "password": "string (必填, 8-32位, 需包含字母和数字)",
  "email": "string (选填, 有效邮箱格式)",
  "nickname": "string (选填)"
}
```

**响应** `201 Created`:
```json
{
  "id": 2,
  "username": "testuser",
  "email": "test@example.com",
  "nickname": "Test User",
  "role": "user",
  "status": "active",
  "must_change_password": false,
  "created_at": "2026-03-20T10:00:00"
}
```

**错误码**:
- `400`: 用户名已注册 / 邮箱已注册 / 密码格式不正确

---

### 2. 用户登录

**POST** `/api/auth/login`

用户登录，获取 JWT 访问令牌。

**请求体**:
```json
{
  "username": "string (必填)",
  "password": "string (必填)",
  "remember_me": "boolean (选填, 默认 false)"
}
```

**响应** `200 OK`:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token 有效期**:
- 普通登录: 24 小时
- 记住我: 7 天

**错误码**:
- `401`: 用户名或密码错误
- `403`: 账户已被锁定（连续5次登录失败后锁定15分钟）

---

### 3. 退出登录

**POST** `/api/auth/logout`

使当前 Token 失效。

**请求头**:
```
Authorization: Bearer <token>
```

**响应** `200 OK`:
```json
{
  "message": "Successfully logged out"
}
```

---

### 4. 获取当前用户信息

**GET** `/api/auth/me`

获取已登录用户的详细信息。

**请求头**:
```
Authorization: Bearer <token>
```

**响应** `200 OK`:
```json
{
  "id": 1,
  "username": "admin",
  "email": null,
  "nickname": "Administrator",
  "role": "admin",
  "status": "active",
  "must_change_password": true,
  "created_at": "2026-03-20T08:00:00"
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 用户唯一标识 |
| username | string | 用户名 |
| email | string | 邮箱（可为空）|
| nickname | string | 昵称 |
| role | string | 角色: `admin` / `user` |
| status | string | 状态: `active` / `disabled` |
| must_change_password | boolean | 是否需要强制修改密码 |
| created_at | datetime | 注册时间 |

---

### 5. 修改密码

**PUT** `/api/auth/password`

修改当前用户的密码。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "old_password": "string (必填, 需验证旧密码)",
  "new_password": "string (必填, 8-32位)"
}
```

**响应** `200 OK`:
```json
{
  "message": "Password changed successfully"
}
```

**错误码**:
- `400`: 旧密码不正确

---

### 6. 强制修改密码（首次登录）

**PUT** `/api/auth/password/admin`

首次登录或被强制修改密码时使用此接口，不需要旧密码验证。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "old_password": "string (选填, 强制修改时可不填)",
  "new_password": "string (必填, 8-32位)"
}
```

**响应** `200 OK`:
```json
{
  "message": "Password changed successfully"
}
```

---

## 任务接口

### 7. 获取任务列表

**GET** `/api/tasks`

获取当前用户的任务列表，支持分页、筛选和搜索。

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 任务状态: `todo` / `in_progress` / `completed` / `cancelled` |
| priority | string | 否 | 优先级: `high` / `medium` / `low` |
| search | string | 否 | 关键词搜索（匹配标题和描述）|
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页条数，默认 20，范围 10-50 |

**响应** `200 OK`:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "完成任务A",
      "description": "详细描述...",
      "priority": "high",
      "status": "todo",
      "due_date": "2026-03-25T18:00:00",
      "sort_order": 0,
      "created_at": "2026-03-20T10:00:00",
      "updated_at": "2026-03-20T10:00:00",
      "attachments": [
        {
          "id": 1,
          "file_name": "document.pdf",
          "file_size": 1024000,
          "file_type": "other",
          "mime_type": "application/pdf",
          "created_at": "2026-03-20T11:00:00"
        }
      ]
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

---

### 8. 获取任务详情

**GET** `/api/tasks/{task_id}`

获取指定任务的详细信息。

**路径参数**:
- `task_id`: 任务 ID

**响应** `200 OK`:
```json
{
  "id": 1,
  "title": "完成任务A",
  "description": "详细描述...",
  "priority": "high",
  "status": "todo",
  "due_date": "2026-03-25T18:00:00",
  "sort_order": 0,
  "created_at": "2026-03-20T10:00:00",
  "updated_at": "2026-03-20T10:00:00",
  "attachments": [...]
}
```

**错误码**:
- `404`: 任务不存在

---

### 9. 创建任务

**POST** `/api/tasks`

创建新任务。

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "string (必填, 最大100字符)",
  "description": "string (选填, 最大2000字符)",
  "priority": "string (选填, 默认 medium, 值: high/medium/low)",
  "due_date": "datetime (选填, ISO8601格式)"
}
```

**响应** `201 Created`:
```json
{
  "id": 2,
  "title": "新任务",
  "description": null,
  "priority": "medium",
  "status": "todo",
  "due_date": null,
  "sort_order": 1,
  "created_at": "2026-03-20T12:00:00",
  "updated_at": "2026-03-20T12:00:00",
  "attachments": []
}
```

---

### 10. 更新任务

**PUT** `/api/tasks/{task_id}`

更新任务信息。

**路径参数**:
- `task_id`: 任务 ID

**请求体**:
```json
{
  "title": "string (选填)",
  "description": "string (选填)",
  "priority": "string (选填, high/medium/low)",
  "due_date": "datetime (选填, null 表示清除)"
}
```

**响应** `200 OK`:
```json
{
  "id": 1,
  "title": "更新后的任务",
  "description": "新的描述",
  "priority": "high",
  "status": "todo",
  "due_date": "2026-03-26T18:00:00",
  "sort_order": 0,
  "created_at": "2026-03-20T10:00:00",
  "updated_at": "2026-03-20T14:00:00",
  "attachments": []
}
```

---

### 11. 删除任务

**DELETE** `/api/tasks/{task_id}`

删除任务（软删除，数据保留）。

**路径参数**:
- `task_id`: 任务 ID

**响应** `200 OK`:
```json
{
  "message": "Task deleted successfully"
}
```

---

### 12. 更新任务状态

**PATCH** `/api/tasks/{task_id}/status`

更新任务状态，支持状态流转校验。

**路径参数**:
- `task_id`: 任务 ID

**请求体**:
```json
{
  "status": "string (必填)"
}
```

**状态流转规则**:
```
待办(todo) → 进行中(in_progress)、已取消(cancelled)
进行中(in_progress) → 已完成(completed)、待办(todo)
已完成(completed) → 无（终态）
已取消(cancelled) → 待办(todo)
```

**响应** `200 OK`:
```json
{
  "id": 1,
  "status": "in_progress",
  ...
}
```

**错误码**:
- `400`: 无效的状态转换

---

### 13. 拖拽排序

**PUT** `/api/tasks/sort`

保存拖拽排序后的任务顺序。

**请求体**:
```json
{
  "task_ids": [3, 1, 2, 5, 4]
}
```

**说明**: 数组顺序即为新的排序顺序。

**响应** `200 OK`:
```json
{
  "message": "Tasks reordered successfully"
}
```

---

### 14. 获取任务统计

**GET** `/api/tasks/stats`

获取当前用户的任务统计信息。

**响应** `200 OK`:
```json
{
  "total": 50,
  "todo": 15,
  "in_progress": 10,
  "completed": 20,
  "cancelled": 5,
  "due_today": 3,
  "overdue": 2
}
```

**字段说明**:
| 字段 | 说明 |
|------|------|
| total | 任务总数 |
| todo | 待办任务数 |
| in_progress | 进行中任务数 |
| completed | 已完成任务数 |
| cancelled | 已取消任务数 |
| due_today | 今日到期任务数 |
| overdue | 已过期任务数（未完成且已过截止时间）|

---

## 附件接口

### 15. 上传附件

**POST** `/api/tasks/{task_id}/attachments`

上传任务附件。

**路径参数**:
- `task_id`: 任务 ID

**请求格式**: `multipart/form-data`

**请求体**:
- `file`: 文件（必填）

**文件限制**:
| 类型 | 默认大小限制 |
|------|-------------|
| 图片 | 10 MB |
| 视频 | 200 MB |
| 其他 | 50 MB |

**支持的格式**:
- 图片: JPG, PNG, GIF, BMP, WebP
- 视频: MP4, AVI, MOV, MKV
- 其他: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, ZIP, RAR

**响应** `201 Created`:
```json
{
  "id": 1,
  "file_name": "report.pdf",
  "file_size": 2048000,
  "file_type": "other",
  "mime_type": "application/pdf",
  "created_at": "2026-03-20T15:00:00"
}
```

**错误码**:
- `400`: 文件大小超限 / 超过最大附件数（10个）

---

### 16. 获取任务附件列表

**GET** `/api/tasks/{task_id}/attachments`

获取指定任务的所有附件。

**响应** `200 OK`:
```json
[
  {
    "id": 1,
    "file_name": "report.pdf",
    "file_size": 2048000,
    "file_type": "other",
    "mime_type": "application/pdf",
    "created_at": "2026-03-20T15:00:00"
  }
]
```

---

### 17. 下载附件

**GET** `/api/attachments/{attachment_id}/download`

下载指定附件。

**路径参数**:
- `attachment_id`: 附件 ID

**响应**: 文件流

**响应头**:
```
Content-Type: {mime_type}
Content-Disposition: attachment; filename="{file_name}"
```

---

### 18. 删除附件

**DELETE** `/api/attachments/{attachment_id}`

删除指定附件（同时删除物理文件）。

**路径参数**:
- `attachment_id`: 附件 ID

**响应** `200 OK`:
```json
{
  "message": "Attachment deleted successfully"
}
```

---

## 管理员接口

> 以下接口需要管理员权限 (`role: admin`)

### 19. 获取用户列表

**GET** `/api/admin/users`

获取所有注册用户列表。

**响应** `200 OK`:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": null,
    "nickname": "Administrator",
    "role": "admin",
    "status": "active",
    "must_change_password": false,
    "created_at": "2026-03-20T08:00:00"
  },
  {
    "id": 2,
    "username": "user1",
    "email": "user1@example.com",
    "nickname": "User One",
    "role": "user",
    "status": "active",
    "must_change_password": false,
    "created_at": "2026-03-20T09:00:00"
  }
]
```

---

### 20. 启用/禁用用户

**PATCH** `/api/admin/users/{user_id}`

启用或禁用指定用户账户。

**路径参数**:
- `user_id`: 用户 ID

**查询参数**:
- `enabled`: boolean (必填, true=启用, false=禁用)

**响应** `200 OK`:
```json
{
  "id": 2,
  "username": "user1",
  "status": "disabled",
  ...
}
```

---

### 21. 重置用户密码

**POST** `/api/admin/users/{user_id}/reset-password`

重置指定用户的密码。

**路径参数**:
- `user_id`: 用户 ID

**查询参数**:
- `new_password`: string (必填, 8-32位)

**响应** `200 OK`:
```json
{
  "id": 2,
  "username": "user1",
  "must_change_password": true,
  ...
}
```

**说明**: 重置后该用户首次登录时会被强制修改密码。

---

### 22. 获取系统统计

**GET** `/api/admin/stats`

获取系统级别的统计数据。

**响应** `200 OK`:
```json
{
  "total_users": 15,
  "total_tasks": 200,
  "status_counts": {
    "todo": 50,
    "in_progress": 30,
    "completed": 100,
    "cancelled": 20
  }
}
```

---

### 23. 获取系统配置

**GET** `/api/admin/config`

获取系统配置信息。

**响应** `200 OK`:
```json
{
  "image_max_size": 10485760,
  "video_max_size": 209715200,
  "other_max_size": 52428800,
  "max_attachments_per_task": 10
}
```

**单位说明**: 所有大小限制均以字节为单位。

---

### 24. 更新系统配置

**PUT** `/api/admin/config`

更新系统配置。

**请求体**:
```json
{
  "image_max_size": 15728640,
  "video_max_size": 314572800,
  "other_max_size": 73400320,
  "max_attachments_per_task": 15
}
```

**说明**: 配置修改后即时生效，已上传的文件不受影响。

**响应** `200 OK`:
```json
{
  "message": "Configuration updated successfully"
}
```

---

## 附录

### 错误码汇总

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 / Token 无效 |
| 403 | 权限不足 / 账户被锁定 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 状态码说明

**任务状态 (status)**:
| 状态 | 值 | 说明 |
|------|------|------|
| 待办 | todo | 新创建的任务默认状态 |
| 进行中 | in_progress | 正在处理的任务 |
| 已完成 | completed | 已完成的任务（终态）|
| 已取消 | cancelled | 已取消的任务（可恢复）|

**优先级 (priority)**:
| 优先级 | 值 | 标签颜色 |
|--------|------|---------|
| 高 | high | 红色 |
| 中 | medium | 橙色 |
| 低 | low | 绿色 |

**附件类型 (file_type)**:
| 类型 | 值 | 说明 |
|------|------|------|
| 图片 | image | JPG, PNG, GIF, BMP, WebP |
| 视频 | video | MP4, AVI, MOV, MKV |
| 其他 | other | PDF, DOC, XLS, PPT, TXT, ZIP, RAR |
