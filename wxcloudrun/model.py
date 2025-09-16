from datetime import datetime

from wxcloudrun import db
from sqlalchemy.sql import func


# 计数表
class Counters(db.Model):
    # 设置结构体表格名称
    __tablename__ = 'Counters'

    # 设定结构体对应表格的字段
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=1)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=func.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now())


# 封面图片表
class CoverPicture(db.Model):
    __tablename__ = 'cover_picture'
    
    id = db.Column(db.Integer, primary_key=True)
    picture_name = db.Column(db.String(255), nullable=False, unique=True)
    file_url = db.Column(db.String(500), nullable=False)
    primary_cover = db.Column(db.Boolean, default=False)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=func.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now())


# 用户表
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(100), nullable=False, unique=True)  # WeChat ID
    user_name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text)
    role = db.Column(db.Enum('ADMIN', 'VIP', 'GUEST'), default='GUEST')
    extra_message = db.Column(db.Text)
    created_at = db.Column('createdAt', db.TIMESTAMP, nullable=False, default=func.now())
    updated_at = db.Column('updatedAt', db.TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now())
