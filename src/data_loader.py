import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class ESDataLoader:
    """Elasticsearch诊断数据加载器"""
    
    def __init__(self, data_dir: str):
        """
        初始化数据加载器
        
        Args:
            data_dir: 诊断数据目录路径
        """
        self.data_dir = data_dir
        self.data_cache = {}
    
    def load_json_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        加载JSON文件
        
        Args:
            filename: JSON文件名
            
        Returns:
            解析后的JSON数据，如果文件不存在或解析失败返回None
        """
        if filename in self.data_cache:
            return self.data_cache[filename]
        
        file_path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"警告: 文件 {filename} 不存在")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.data_cache[filename] = data
                return data
        except json.JSONDecodeError as e:
            print(f"错误: 解析文件 {filename} 失败: {e}")
            return None
        except Exception as e:
            print(f"错误: 读取文件 {filename} 失败: {e}")
            return None
    
    def get_cluster_health(self) -> Dict[str, Any]:
        """获取集群健康信息"""
        return self.load_json_file('cluster_health.json')
    
    def get_cluster_settings(self) -> Dict[str, Any]:
        """获取集群设置信息"""
        return self.load_json_file('cluster_settings.json')
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """获取集群统计信息"""
        return self.load_json_file('cluster_stats.json')
    
    def get_licenses(self) -> Optional[Dict[str, Any]]:
        """获取许可证信息"""
        return self.load_json_file('licenses.json')
    
    def get_manifest(self) -> Optional[Dict[str, Any]]:
        """获取清单信息"""
        return self.load_json_file('manifest.json')
    
    def get_nodes(self) -> Optional[Dict[str, Any]]:
        """获取节点信息"""
        return self.load_json_file('nodes.json')
    
    def get_nodes_stats(self) -> Optional[Dict[str, Any]]:
        """获取节点统计信息"""
        return self.load_json_file('nodes_stats.json')
    
    def get_indices_stats(self) -> Optional[Dict[str, Any]]:
        """获取索引统计信息"""
        return self.load_json_file('indices_stats.json')
    
    def get_indices(self) -> Optional[Dict[str, Any]]:
        """获取索引信息"""
        return self.load_json_file('indices.json')
    
    def get_settings(self) -> Optional[Dict[str, Any]]:
        """获取设置信息"""
        return self.load_json_file('settings.json')
    
    def format_bytes(self, bytes_value: int) -> str:
        """
        格式化字节数为人类可读格式
        
        Args:
            bytes_value: 字节数
            
        Returns:
            格式化后的字符串
        """
        if bytes_value is None:
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def format_timestamp(self, timestamp_ms: int) -> str:
        """
        格式化时间戳
        
        Args:
            timestamp_ms: 毫秒时间戳
            
        Returns:
            格式化后的时间字符串
        """
        if timestamp_ms is None:
            return "N/A"
        
        try:
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return "Invalid timestamp" 