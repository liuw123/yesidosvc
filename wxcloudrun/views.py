from datetime import datetime
import os
from flask import render_template, request, send_file, abort
from urllib.parse import unquote
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response


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


@app.route('/pictures/list', methods=['GET'])
def get_pictures_list():
    """
    获取图片列表
    :return: 返回所有图片的名称列表
    """
    try:
        pictures_dir = os.path.join(os.getcwd(), 'resources', 'pictures')
        
        # 检查目录是否存在
        if not os.path.exists(pictures_dir):
            return make_err_response('图片目录不存在')
        
        # 获取目录下所有文件
        files = os.listdir(pictures_dir)
        
        # 过滤出图片文件（可以根据需要添加更多图片格式）
        picture_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        pictures = []
        
        for file in files:
            if os.path.isfile(os.path.join(pictures_dir, file)):
                _, ext = os.path.splitext(file.lower())
                if ext in picture_extensions:
                    pictures.append(file)
        
        return make_succ_response({
            'pictures': pictures,
            'total': len(pictures)
        })
        
    except Exception as e:
        return make_err_response(f'获取图片列表失败: {str(e)}')


@app.route('/pictures/<path:picture_name>', methods=['GET'])
def download_picture(picture_name):
    """
    下载图片
    :param picture_name: 图片名称（URL编码）
    :return: 图片文件
    """
    try:
        # URL解码图片名称
        decoded_name = unquote(picture_name)
        
        # 构建图片文件路径
        pictures_dir = os.path.join(os.getcwd(), 'resources', 'pictures')
        file_path = os.path.join(pictures_dir, decoded_name)
        
        # 安全检查：确保文件路径在pictures目录内
        if not os.path.abspath(file_path).startswith(os.path.abspath(pictures_dir)):
            abort(403)  # 禁止访问
        
        # 检查文件是否存在
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            abort(404)  # 文件不存在
        
        # 返回文件
        return send_file(file_path, as_attachment=True, download_name=decoded_name)
        
    except Exception as e:
        return make_err_response(f'下载图片失败: {str(e)}')
