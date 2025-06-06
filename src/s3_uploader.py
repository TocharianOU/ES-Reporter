import os
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

class S3Uploader:
    """S3文件上传器 (使用MinIO Python SDK)"""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        if config:
            self.bucket_name = config.get('bucket_name')
            self.access_key = config.get('access_key')
            self.secret_key = config.get('secret_key')
            self.endpoint = config.get('endpoint')
            self.secure = config.get('secure', False)
        else:
            self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
            self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
            self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            endpoint_url = os.getenv('AWS_ENDPOINT_URL', '')
            
            if endpoint_url.startswith('https://'):
                self.endpoint = endpoint_url[8:]
                self.secure = True
            elif endpoint_url.startswith('http://'):
                self.endpoint = endpoint_url[7:]
                self.secure = False
            else:
                self.endpoint = endpoint_url
                self.secure = False
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            if not all([self.endpoint, self.access_key, self.secret_key]):
                logger.warning("MinIO配置不完整，跳过客户端初始化")
                return
            
            self.client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            logger.info(f"MinIO客户端初始化成功，endpoint: {self.endpoint}, secure: {self.secure}")
        except Exception as e:
            logger.error(f"MinIO客户端初始化失败: {e}")
            self.client = None
    
    def is_configured(self) -> bool:
        return (self.client is not None 
                and self.bucket_name is not None 
                and self.bucket_name.strip() != "")
    
    def create_folder_with_file_hash(self, file_path: str) -> str:
        """
        创建基于文件哈希的文件夹名
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件的SHA256哈希值前16位
        """
        if not os.path.exists(file_path):
            # 如果文件不存在，使用时间戳作为备选
            return str(int(time.time()))
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # 分块读取文件以处理大文件
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        # 返回哈希值的前16位（足够唯一且不会太长）
        return sha256_hash.hexdigest()[:16]
    
    def upload_file(self, local_file_path: str, s3_key: str, 
                   metadata: Optional[Dict[str, str]] = None) -> bool:
        if not self.is_configured():
            logger.error("S3未正确配置，跳过上传")
            return False
        
        if not os.path.exists(local_file_path):
            logger.error(f"本地文件不存在: {local_file_path}")
            return False
        
        try:
            # 假设桶已存在，不尝试创建
            content_type = "application/octet-stream"
            if local_file_path.endswith('.zip'):
                content_type = 'application/zip'
            elif local_file_path.endswith('.html'):
                content_type = 'text/html'
            elif local_file_path.endswith('.md'):
                content_type = 'text/markdown'
            
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=s3_key,
                file_path=local_file_path,
                content_type=content_type,
                metadata=metadata or {}
            )
            
            logger.info(f"文件上传成功: {local_file_path} -> s3://{self.bucket_name}/{s3_key}")
            return True
            
        except FileNotFoundError:
            logger.error(f"本地文件未找到: {local_file_path}")
            return False
        except S3Error as e:
            logger.error(f"S3上传失败: {e}")
            return False
        except Exception as e:
            logger.error(f"上传过程中发生未知错误: {e}")
            return False
    
    def upload_zip_immediately(self, zip_file_path: str, original_filename: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                'success': False,
                'message': 'S3未配置',
                'folder': None,
                's3_key': None
            }
        
        # 创建基于文件哈希的文件夹名
        folder_name = self.create_folder_with_file_hash(zip_file_path)
        current_time = datetime.now().isoformat()
        metadata = {
            'upload-time': current_time,
            'original-filename': original_filename,
            'folder': folder_name,
            'file-hash': folder_name,
            'type': 'diagnostic-zip'
        }
        
        zip_s3_key = f"{folder_name}/{original_filename}"
        upload_success = self.upload_file(zip_file_path, zip_s3_key, metadata)
        
        return {
            'success': upload_success,
            'message': f'ZIP文件上传{"成功" if upload_success else "失败"}',
            'folder': folder_name,
            's3_key': zip_s3_key if upload_success else None
        }
    
    def upload_reports_to_folder(self, folder_name: str, markdown_path: str, 
                               html_path: str) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                'success': False,
                'message': 'S3未配置',
                'files': {}
            }
        
        current_time = datetime.now().isoformat()
        metadata = {
            'upload-time': current_time,
            'folder': folder_name,
            'file-hash': folder_name,
            'type': 'report'
        }
        
        upload_results = {}
        all_success = True
        
        if os.path.exists(markdown_path):
            md_filename = os.path.basename(markdown_path)
            md_s3_key = f"{folder_name}/{md_filename}"
            md_result = self.upload_file(markdown_path, md_s3_key, metadata)
            upload_results['markdown'] = {
                'success': md_result,
                's3_key': md_s3_key if md_result else None
            }
            all_success = all_success and md_result
        
        if os.path.exists(html_path):
            html_filename = os.path.basename(html_path)
            html_s3_key = f"{folder_name}/{html_filename}"
            html_result = self.upload_file(html_path, html_s3_key, metadata)
            upload_results['html'] = {
                'success': html_result,
                's3_key': html_s3_key if html_result else None
            }
            all_success = all_success and html_result
        
        return {
            'success': all_success,
            'message': f'报告上传{"成功" if all_success else "失败"}到文件夹: {folder_name}',
            'files': upload_results
        }
    
    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                'success': False,
                'message': 'S3未配置',
                'details': {}
            }
        
        try:
            # 测试列出桶中的对象（而不是检查桶是否存在）
            objects = list(self.client.list_objects(self.bucket_name))
            
            return {
                'success': True,
                'message': 'MinIO连接测试成功',
                'details': {
                    'bucket': self.bucket_name,
                    'endpoint': self.endpoint,
                    'secure': self.secure,
                    'accessible': True
                }
            }
        except S3Error as e:
            error_details = {
                'bucket': self.bucket_name,
                'endpoint': self.endpoint,
                'error_code': e.code if hasattr(e, 'code') else 'Unknown'
            }
            return {
                'success': False,
                'message': f'MinIO连接失败: {e}',
                'details': error_details
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'连接测试时发生未知错误: {e}',
                'details': {
                    'bucket': self.bucket_name,
                    'endpoint': self.endpoint
                }
            } 