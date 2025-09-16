import logging

from sqlalchemy.exc import OperationalError

from wxcloudrun import db
from wxcloudrun.model import Counters, CoverPicture, User

# 初始化日志
logger = logging.getLogger('log')


def query_counterbyid(id):
    """
    根据ID查询Counter实体
    :param id: Counter的ID
    :return: Counter实体
    """
    try:
        return Counters.query.filter(Counters.id == id).first()
    except OperationalError as e:
        logger.info("query_counterbyid errorMsg= {} ".format(e))
        return None


def delete_counterbyid(id):
    """
    根据ID删除Counter实体
    :param id: Counter的ID
    """
    try:
        counter = Counters.query.get(id)
        if counter is None:
            return
        db.session.delete(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("delete_counterbyid errorMsg= {} ".format(e))


def insert_counter(counter):
    """
    插入一个Counter实体
    :param counter: Counters实体
    """
    try:
        db.session.add(counter)
        db.session.commit()
    except OperationalError as e:
        logger.info("insert_counter errorMsg= {} ".format(e))


def update_counterbyid(counter):
    """
    根据ID更新counter的值
    :param counter实体
    """
    try:
        counter = query_counterbyid(counter.id)
        if counter is None:
            return
        db.session.flush()
        db.session.commit()
    except OperationalError as e:
        logger.info("update_counterbyid errorMsg= {} ".format(e))


# ==================== Cover Picture DAO ====================

def insert_cover_picture(cover_picture):
    """
    插入封面图片记录
    :param cover_picture: CoverPicture实体
    """
    try:
        db.session.add(cover_picture)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_cover_picture errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def query_cover_picture_by_name(picture_name):
    """
    根据图片名称查询封面图片
    :param picture_name: 图片名称
    :return: CoverPicture实体
    """
    try:
        return CoverPicture.query.filter(CoverPicture.picture_name == picture_name).first()
    except OperationalError as e:
        logger.info("query_cover_picture_by_name errorMsg= {} ".format(e))
        return None


def query_all_cover_pictures():
    """
    查询所有封面图片
    :return: CoverPicture实体列表
    """
    try:
        return CoverPicture.query.order_by(CoverPicture.created_at.desc()).all()
    except OperationalError as e:
        logger.info("query_all_cover_pictures errorMsg= {} ".format(e))
        return []


def delete_cover_picture_by_name(picture_name):
    """
    根据图片名称删除封面图片
    :param picture_name: 图片名称
    """
    try:
        cover_picture = CoverPicture.query.filter(CoverPicture.picture_name == picture_name).first()
        if cover_picture is None:
            return False
        db.session.delete(cover_picture)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_cover_picture_by_name errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def update_primary_cover(picture_name, is_primary):
    """
    更新封面图片的主封面状态
    :param picture_name: 图片名称
    :param is_primary: 是否为主封面
    """
    try:
        # 如果设置为主封面，先将其他所有图片设置为非主封面
        if is_primary:
            CoverPicture.query.update({CoverPicture.primary_cover: False})
        
        # 更新指定图片的主封面状态
        cover_picture = CoverPicture.query.filter(CoverPicture.picture_name == picture_name).first()
        if cover_picture:
            cover_picture.primary_cover = is_primary
            db.session.commit()
            return True
        return False
    except OperationalError as e:
        logger.info("update_primary_cover errorMsg= {} ".format(e))
        db.session.rollback()
        return False


# ==================== User DAO ====================

def insert_user(user):
    """
    插入用户记录
    :param user: User实体
    """
    try:
        db.session.add(user)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("insert_user errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def query_user_by_id(user_id):
    """
    根据ID查询用户
    :param user_id: 用户ID
    :return: User实体
    """
    try:
        return User.query.filter(User.id == user_id).first()
    except OperationalError as e:
        logger.info("query_user_by_id errorMsg= {} ".format(e))
        return None


def query_user_by_userid(userid):
    """
    根据微信ID查询用户
    :param userid: 微信ID
    :return: User实体
    """
    try:
        return User.query.filter(User.userid == userid).first()
    except OperationalError as e:
        logger.info("query_user_by_userid errorMsg= {} ".format(e))
        return None


def query_all_users():
    """
    查询所有用户
    :return: User实体列表
    """
    try:
        return User.query.order_by(User.created_at.desc()).all()
    except OperationalError as e:
        logger.info("query_all_users errorMsg= {} ".format(e))
        return []


def update_user(user):
    """
    更新用户信息
    :param user: User实体
    """
    try:
        existing_user = User.query.filter(User.id == user.id).first()
        if existing_user is None:
            return False
        
        existing_user.user_name = user.user_name
        existing_user.comment = user.comment
        existing_user.role = user.role
        existing_user.extra_message = user.extra_message
        existing_user.updated_at = user.updated_at
        
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("update_user errorMsg= {} ".format(e))
        db.session.rollback()
        return False


def delete_user_by_id(user_id):
    """
    根据ID删除用户
    :param user_id: 用户ID
    """
    try:
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            return False
        db.session.delete(user)
        db.session.commit()
        return True
    except OperationalError as e:
        logger.info("delete_user_by_id errorMsg= {} ".format(e))
        db.session.rollback()
        return False
