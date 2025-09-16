import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')

# 腾讯云COS配置
COS_SECRET_ID = os.environ.get("COS_SECRET_ID", "your_secret_id")
COS_SECRET_KEY = os.environ.get("COS_SECRET_KEY", "your_secret_key")
COS_REGION = os.environ.get("COS_REGION", "ap-beijing")
COS_BUCKET_NAME = os.environ.get("COS_BUCKET_NAME", "wechat-miniprogram")

# 管理员密钥
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "admin_secret_key_2024")
