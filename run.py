# 创建应用实例
import sys

from wxcloudrun import app
from init_db import init_database

# 启动Flask Web服务
if __name__ == '__main__':
    init_database()
    app.run(host=sys.argv[1], port=sys.argv[2])
