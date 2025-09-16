#!/usr/bin/env python3
"""
数据库初始化脚本
创建所需的数据库表
"""

from wxcloudrun import app, db
from wxcloudrun.model import Counters, CoverPicture, User

def init_database():
    """初始化数据库表"""
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("数据库表创建成功！")
            
            # 打印创建的表信息
            print("\n已创建的表:")
            print("- Counters (计数表)")
            print("- cover_picture (封面图片表)")
            print("- users (用户表)")
            
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    print("开始初始化数据库...")
    if init_database():
        print("\n数据库初始化完成！")
    else:
        print("\n数据库初始化失败！")
