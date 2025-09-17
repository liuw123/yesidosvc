from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import io
from PIL import Image
import os
import uuid
from datetime import datetime
import config
import logging

logger = logging.getLogger('log')

class COSClient:
    def __init__(self):
        """初始化腾讯云COS客户端"""
        cos_config = CosConfig(
            Region=config.COS_REGION,
            SecretId=config.COS_SECRET_ID,
            SecretKey=config.COS_SECRET_KEY,
            Scheme='https'
        )
        self.client = CosS3Client(cos_config)
        self.bucket = config.COS_BUCKET_NAME
    
    def resize_image(self, image_data, max_size=1440):
        """
        调整图片大小，保持宽高比，确保最大边不超过max_size
        :param image_data: 图片二进制数据
        :param max_size: 最大尺寸，默认1440px
        :return: 调整后的图片二进制数据
        """
        try:
            # 打开图片
            image = Image.open(io.BytesIO(image_data))
            
            # 获取原始尺寸
            width, height = image.size
            
            # 如果图片尺寸已经符合要求，直接返回
            if width <= max_size and height <= max_size:
                return image_data
            
            # 计算新尺寸，保持宽高比
            if width > height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)
            
            # 调整图片大小
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存到内存
            output = io.BytesIO()
            # 保持原始格式，如果是JPEG则保存为JPEG，PNG则保存为PNG
            format = image.format if image.format else 'JPEG'
            if format == 'JPEG':
                resized_image.save(output, format=format, quality=85, optimize=True)
            else:
                resized_image.save(output, format=format, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"图片调整大小失败: {str(e)}")
            return image_data  # 如果调整失败，返回原始数据
    
    def upload_cover_image(self, file_data, original_filename, override_filename=False):
        """
        上传封面图片到腾讯云COS
        :param file_data: 文件二进制数据
        :param original_filename: 原始文件名
        :return: (success, file_url, picture_name) 或 (success, error_message, None)
        """
        try:
            # 调整图片大小
            resized_data = self.resize_image(file_data)
            
            # 生成唯一的文件名
            file_ext = os.path.splitext(original_filename)[1].lower()
            if not file_ext:
                file_ext = '.jpg'  # 默认扩展名
            
            # 使用时间戳和UUID生成唯一文件名
            picture_name = original_filename
            if override_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                picture_name = f"cover_{timestamp}_{unique_id}{file_ext}"
            
            # COS中的文件路径
            cos_key = f"covers/{picture_name}"
            
            # 上传到COS
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=resized_data,
                Key=cos_key,
                ContentType=self._get_content_type(file_ext)
            )
            if 'ETag' in response:
                # 生成文件访问URL
                file_url = f"cloud://{config.ENV_ID}.{config.COS_BUCKET}/{cos_key}"
                return True, file_url, picture_name
            else:
                return False, f"上传失败 {response}", None
                
        except Exception as e:
            return False, f"上传失败: {str(e)}", None
    
    def delete_cover_image(self, picture_name):
        """
        从腾讯云COS删除封面图片
        :param picture_name: 图片名称
        :return: (success, message)
        """
        try:
            cos_key = f"covers/{picture_name}"
            response = self.client.delete_object(
                Bucket=self.bucket,
                Key=cos_key
            )
            
            if response is not None:
                return True, "删除成功"
            else:
                return False, f"删除失败 {response}"
                
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def check_image_exists(self, picture_name):
        """
        检查图片是否存在于COS中
        :param picture_name: 图片名称
        :return: bool
        """
        try:
            cos_key = f"covers/{picture_name}"
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=cos_key
            )
            return response is not None
        except Exception as e:
            logger.error(f"检查文件存在性失败: {str(e)}")
            return False
    
    def _get_content_type(self, file_ext):
        """
        根据文件扩展名获取Content-Type
        :param file_ext: 文件扩展名
        :return: Content-Type字符串
        """
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return content_types.get(file_ext.lower(), 'image/jpeg')


# 创建全局COS客户端实例
cos_client = COSClient()
