# YesidoSvc API Documentation

## Overview
This document describes the APIs implemented for the WeChat miniprogram backend service, including cover picture management and user management functionality.

## Authentication
Admin-only APIs require an `Admin-Secret` header with the configured admin secret key.

## Cover Picture APIs

### 1. Upload Cover Picture
**Endpoint:** `POST /api/cover/upload`  
**Authentication:** Admin required  
**Content-Type:** `multipart/form-data`

**Headers:**
```
Admin-Secret: your_admin_secret_key
```

**Form Data:**
- `file`: Image file (required) - Supported formats: jpg, jpeg, png, gif, bmp, webp
- `primary_cover`: Boolean (optional) - Set to "true" to mark as primary cover, default is "false"

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "picture_name": "cover_20241216_123456_abcd1234.jpg",
    "file_url": "https://bucket.oss-endpoint.com/covers/cover_20241216_123456_abcd1234.jpg",
    "primary_cover": false,
    "major_color": "#FF5733"
  }
}
```

**Features:**
- Automatically resizes images to max 1440px while maintaining aspect ratio
- Generates unique filename with timestamp and UUID
- Uploads to Tencent COS and stores metadata in database
- Extracts major color from image using ColorThief algorithm
- If marked as primary cover, automatically unmarks other primary covers

### 2. Delete Cover Picture
**Endpoint:** `DELETE /api/cover/{picture_name}`  
**Authentication:** Admin required

**Headers:**
```
Admin-Secret: your_admin_secret_key
```

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "message": "删除成功"
  }
}
```

### 3. List Cover Pictures
**Endpoint:** `GET /api/cover/list`  
**Authentication:** None required

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "pictures": [
      {
        "id": 1,
        "picture_name": "cover_20241216_123456_abcd1234.jpg",
        "file_url": "https://bucket.oss-endpoint.com/covers/cover_20241216_123456_abcd1234.jpg",
        "primary_cover": true,
        "major_color": "#FF5733",
        "created_at": "2024-12-16 12:34:56",
        "updated_at": "2024-12-16 12:34:56"
      }
    ],
    "total": 1
  }
}
```

## User Management APIs

### 1. Create User
**Endpoint:** `POST /api/users`  
**Authentication:** Admin required  
**Content-Type:** `application/json`

**Headers:**
```
Admin-Secret: your_admin_secret_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "userid": "wechat_user_id",
  "user_name": "用户名",
  "comment": "用户备注",
  "role": "GUEST",
  "extra_message": "额外信息"
}
```

**Fields:**
- `userid`: WeChat user ID (required, unique)
- `user_name`: User display name (required)
- `comment`: User comment (optional)
- `role`: User role - "ADMIN", "VIP", or "GUEST" (optional, default: "GUEST")
- `extra_message`: Additional information (optional)

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "id": 1,
    "userid": "wechat_user_id",
    "user_name": "用户名",
    "comment": "用户备注",
    "role": "GUEST",
    "extra_message": "额外信息",
    "created_at": "2024-12-16 12:34:56"
  }
}
```

### 2. List Users
**Endpoint:** `GET /api/users`  
**Authentication:** Admin required

**Headers:**
```
Admin-Secret: your_admin_secret_key
```

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "users": [
      {
        "id": 1,
        "userid": "wechat_user_id",
        "user_name": "用户名",
        "comment": "用户备注",
        "role": "GUEST",
        "extra_message": "额外信息",
        "created_at": "2024-12-16 12:34:56",
        "updated_at": "2024-12-16 12:34:56"
      }
    ],
    "total": 1
  }
}
```

### 3. Get User by ID
**Endpoint:** `GET /api/users/{user_id}`  
**Authentication:** Admin required

**Headers:**
```
Admin-Secret: your_admin_secret_key
```

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "id": 1,
    "userid": "wechat_user_id",
    "user_name": "用户名",
    "comment": "用户备注",
    "role": "GUEST",
    "extra_message": "额外信息",
    "created_at": "2024-12-16 12:34:56",
    "updated_at": "2024-12-16 12:34:56"
  }
}
```

### 4. Update User
**Endpoint:** `PUT /api/users/{user_id}`  
**Authentication:** Admin required  
**Content-Type:** `application/json`

**Headers:**
```
Admin-Secret: your_admin_secret_key
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_name": "新用户名",
  "comment": "新备注",
  "role": "VIP",
  "extra_message": "新的额外信息"
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "id": 1,
    "userid": "wechat_user_id",
    "user_name": "新用户名",
    "comment": "新备注",
    "role": "VIP",
    "extra_message": "新的额外信息",
    "updated_at": "2024-12-16 13:45:67"
  }
}
```

### 5. Delete User
**Endpoint:** `DELETE /api/users/{user_id}`  
**Authentication:** Admin required

**Headers:**
```
Admin-Secret: your_admin_secret_key
```

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "message": "删除成功"
  }
}
```

### 6. Get User Info by WeChat ID
**Endpoint:** `GET /api/user/{userid}`  
**Authentication:** None required

**Response:**
```json
{
  "code": 0,
  "errorMsg": "",
  "data": {
    "id": 1,
    "userid": "wechat_user_id",
    "user_name": "用户名",
    "comment": "用户备注",
    "role": "GUEST",
    "extra_message": "额外信息",
    "created_at": "2024-12-16 12:34:56",
    "updated_at": "2024-12-16 12:34:56"
  }
}
```

## Error Response Format
All APIs return errors in the following format:
```json
{
  "code": 1,
  "errorMsg": "Error description",
  "data": null
}
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Set the following environment variables:
```bash
# Database Configuration
export MYSQL_USERNAME="your_mysql_username"
export MYSQL_PASSWORD="your_mysql_password"
export MYSQL_ADDRESS="your_mysql_host:port"

# Tencent COS Configuration
export COS_SECRET_ID="your_cos_secret_id"
export COS_SECRET_KEY="your_cos_secret_key"
export COS_REGION="ap-beijing"
export COS_BUCKET_NAME="your_cos_bucket_name"

# Admin Secret
export ADMIN_SECRET="your_admin_secret_key"
```

### 3. Initialize Database
```bash
python init_db.py
```

### 4. Run the Application
```bash
python run.py
```

## Testing with curl

### Upload Cover Picture
```bash
curl -X POST http://localhost:5000/api/cover/upload \
  -H "Admin-Secret: admin_secret_key_2024" \
  -F "file=@/path/to/image.jpg" \
  -F "primary_cover=true"
```

### List Cover Pictures
```bash
curl -X GET http://localhost:5000/api/cover/list
```

### Create User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Admin-Secret: admin_secret_key_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "userid": "test_wechat_id",
    "user_name": "测试用户",
    "comment": "这是一个测试用户",
    "role": "VIP"
  }'
```

### Get User Info
```bash
curl -X GET http://localhost:5000/api/user/test_wechat_id
```

## Database Schema

### cover_picture Table
- `id`: Primary key (INT, AUTO_INCREMENT)
- `picture_name`: Unique picture name (VARCHAR(255))
- `file_url`: Tencent COS file URL (VARCHAR(500))
- `primary_cover`: Whether it's the primary cover (BOOLEAN)
- `major_color`: Extracted major color in hex format (VARCHAR(7), e.g., #FF5733)
- `createdAt`: Creation timestamp (TIMESTAMP)
- `updatedAt`: Update timestamp (TIMESTAMP)

### users Table
- `id`: Primary key (INT, AUTO_INCREMENT)
- `userid`: WeChat user ID (VARCHAR(100), UNIQUE)
- `user_name`: User display name (VARCHAR(100))
- `comment`: User comment (TEXT)
- `role`: User role ENUM('ADMIN', 'VIP', 'GUEST')
- `extra_message`: Additional information (TEXT)
- `createdAt`: Creation timestamp (TIMESTAMP)
- `updatedAt`: Update timestamp (TIMESTAMP)
