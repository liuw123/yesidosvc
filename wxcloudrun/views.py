from datetime import datetime
import os
from flask import render_template, request, send_file, abort, jsonify
from urllib.parse import unquote
from functools import wraps
from run import app
from wxcloudrun.dao import (
    delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid,
    insert_cover_picture, query_cover_picture_by_name, query_all_cover_pictures, 
    delete_cover_picture_by_name, update_primary_cover,
    insert_user, query_user_by_id, query_user_by_userid, query_all_users, 
    update_user, delete_user_by_id
)
from wxcloudrun.model import Counters, CoverPicture, User
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
from wxcloudrun.cos_client import cos_client
import config


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

# ==================== Admin Authentication Decorator ====================

def admin_required(f):
    """
    管理员权限验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_secret = request.headers.get('Admin-Secret')
        if not admin_secret or admin_secret != config.ADMIN_SECRET:
            return make_err_response('无管理员权限'), 403
        return f(*args, **kwargs)
    return decorated_function


# ==================== Cover Picture APIs ====================

@app.route('/api/cover/upload', methods=['POST'])
@admin_required
def upload_cover_picture():
    """
    上传封面图片 (仅管理员)
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return make_err_response('没有上传文件')
        
        file = request.files['file']
        if file.filename == '':
            return make_err_response('没有选择文件')
        
        # 检查文件类型
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return make_err_response('不支持的文件格式')
        
        # 获取其他参数
        primary_cover = request.form.get('primary_cover', 'false').lower() == 'true'
        overide_filename = request.form.get('override_filename', 'false').lower() == 'true'
        
        # 读取文件数据
        file_data = file.read()
        
        # 上传到COS
        success, result, picture_name = cos_client.upload_cover_image(file_data, file.filename, overide_filename)
        
        if not success:
            return make_err_response(f'上传失败: {result}')
        
        # 保存到数据库
        cover_picture = CoverPicture()
        cover_picture.picture_name = picture_name
        cover_picture.file_url = result
        cover_picture.primary_cover = primary_cover
        cover_picture.created_at = datetime.now()
        cover_picture.updated_at = datetime.now()
        
        if insert_cover_picture(cover_picture):
            # 如果设置为主封面，更新其他图片的主封面状态
            if primary_cover:
                update_primary_cover(picture_name, True)
            
            return make_succ_response({
                'picture_name': picture_name,
                'file_url': result,
                'primary_cover': primary_cover
            })
        else:
            # 如果数据库保存失败，删除COS中的文件
            cos_client.delete_cover_image(picture_name)
            return make_err_response('保存到数据库失败')
            
    except Exception as e:
        return make_err_response(f'上传失败: {str(e)}')


@app.route('/api/cover/<picture_name>', methods=['DELETE'])
@admin_required
def delete_cover_picture(picture_name):
    """
    删除封面图片 (仅管理员)
    """
    try:
        # 查询图片是否存在
        cover_picture = query_cover_picture_by_name(picture_name)
        if not cover_picture:
            return make_err_response('图片不存在')
        
        # 从COS删除文件
        success, message = cos_client.delete_cover_image(picture_name)
        if not success:
            return make_err_response(f'删除COS文件失败: {message}')
        
        # 从数据库删除记录
        if delete_cover_picture_by_name(picture_name):
            return make_succ_response({'message': '删除成功'})
        else:
            return make_err_response('删除数据库记录失败')
            
    except Exception as e:
        return make_err_response(f'删除失败: {str(e)}')


@app.route('/api/cover/list', methods=['GET'])
def list_cover_pictures():
    """
    获取封面图片列表
    """
    try:
        cover_pictures = query_all_cover_pictures()
        
        result = []
        for picture in cover_pictures:
            result.append({
                'id': picture.id,
                'picture_name': picture.picture_name,
                'file_url': picture.file_url,
                'primary_cover': picture.primary_cover,
                'created_at': picture.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': picture.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return make_succ_response({
            'pictures': result,
            'total': len(result)
        })
        
    except Exception as e:
        return make_err_response(f'获取图片列表失败: {str(e)}')


# ==================== User Management APIs ====================

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    """
    创建用户 (仅管理员)
    """
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data or 'userid' not in data or 'user_name' not in data:
            return make_err_response('缺少必需字段: userid, user_name')
        
        # 检查用户是否已存在
        existing_user = query_user_by_userid(data['userid'])
        if existing_user:
            return make_err_response('用户已存在')
        
        # 创建用户
        user = User()
        user.userid = data['userid']
        user.user_name = data['user_name']
        user.comment = data.get('comment', '')
        user.role = data.get('role', 'GUEST')
        user.extra_message = data.get('extra_message', '')
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        
        # 验证角色
        if user.role not in ['ADMIN', 'VIP', 'GUEST']:
            return make_err_response('无效的角色类型')
        
        if insert_user(user):
            return make_succ_response({
                'id': user.id,
                'userid': user.userid,
                'user_name': user.user_name,
                'comment': user.comment,
                'role': user.role,
                'extra_message': user.extra_message,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return make_err_response('创建用户失败')
            
    except Exception as e:
        return make_err_response(f'创建用户失败: {str(e)}')


@app.route('/api/users', methods=['GET'])
@admin_required
def list_users():
    """
    获取用户列表 (仅管理员)
    """
    try:
        users = query_all_users()
        
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'userid': user.userid,
                'user_name': user.user_name,
                'comment': user.comment,
                'role': user.role,
                'extra_message': user.extra_message,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return make_succ_response({
            'users': result,
            'total': len(result)
        })
        
    except Exception as e:
        return make_err_response(f'获取用户列表失败: {str(e)}')


@app.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_by_id(user_id):
    """
    根据ID获取用户信息 (仅管理员)
    """
    try:
        user = query_user_by_id(user_id)
        if not user:
            return make_err_response('用户不存在')
        
        return make_succ_response({
            'id': user.id,
            'userid': user.userid,
            'user_name': user.user_name,
            'comment': user.comment,
            'role': user.role,
            'extra_message': user.extra_message,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return make_err_response(f'获取用户信息失败: {str(e)}')


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_by_id(user_id):
    """
    更新用户信息 (仅管理员)
    """
    try:
        data = request.get_json()
        if not data:
            return make_err_response('缺少请求数据')
        
        # 查询用户是否存在
        existing_user = query_user_by_id(user_id)
        if not existing_user:
            return make_err_response('用户不存在')
        
        # 更新用户信息
        if 'user_name' in data:
            existing_user.user_name = data['user_name']
        if 'comment' in data:
            existing_user.comment = data['comment']
        if 'role' in data:
            if data['role'] not in ['ADMIN', 'VIP', 'GUEST']:
                return make_err_response('无效的角色类型')
            existing_user.role = data['role']
        if 'extra_message' in data:
            existing_user.extra_message = data['extra_message']
        
        existing_user.updated_at = datetime.now()
        
        if update_user(existing_user):
            return make_succ_response({
                'id': existing_user.id,
                'userid': existing_user.userid,
                'user_name': existing_user.user_name,
                'comment': existing_user.comment,
                'role': existing_user.role,
                'extra_message': existing_user.extra_message,
                'updated_at': existing_user.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return make_err_response('更新用户失败')
            
    except Exception as e:
        return make_err_response(f'更新用户失败: {str(e)}')


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user_by_id_api(user_id):
    """
    删除用户 (仅管理员)
    """
    try:
        # 查询用户是否存在
        user = query_user_by_id(user_id)
        if not user:
            return make_err_response('用户不存在')
        
        if delete_user_by_id(user_id):
            return make_succ_response({'message': '删除成功'})
        else:
            return make_err_response('删除用户失败')
            
    except Exception as e:
        return make_err_response(f'删除用户失败: {str(e)}')


@app.route('/api/user/<userid>', methods=['GET'])
def get_user_info(userid):
    """
    获取用户信息 (根据微信ID)
    """
    try:
        user = query_user_by_userid(userid)
        if not user:
            return make_err_response('用户不存在')
        
        return make_succ_response({
            'id': user.id,
            'userid': user.userid,
            'user_name': user.user_name,
            'comment': user.comment,
            'role': user.role,
            'extra_message': user.extra_message,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': user.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return make_err_response(f'获取用户信息失败: {str(e)}')
