#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Elasticsearch 集群检查器
提供ES集群连接、健康检查和数据收集功能
"""

import json
import requests
import urllib3
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ElasticsearchInspector:
    """Elasticsearch 集群检查器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化ES检查器
        
        Args:
            config: ES连接配置
                - host: ES主机地址
                - port: ES端口
                - username: 用户名(可选)
                - password: 密码(可选)
                - use_ssl: 是否使用SSL
                - verify_certs: 是否验证证书
        """
        self.config = config
        self.base_url = self._build_base_url()
        self.session = self._create_session()
    
    def _build_base_url(self) -> str:
        """构建ES基础URL"""
        protocol = "https" if self.config.get('use_ssl', False) else "http"
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 9200)
        return f"{protocol}://{host}:{port}"
    
    def _create_session(self) -> requests.Session:
        """创建HTTP会话"""
        session = requests.Session()
        
        # 设置认证
        username = self.config.get('username')
        password = self.config.get('password')
        if username and password:
            session.auth = (username, password)
        
        # SSL设置
        if not self.config.get('verify_certs', True):
            session.verify = False
        
        # 设置超时
        session.timeout = 30
        
        return session
    
    def _make_request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
        """发送HTTP请求到ES"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"ES请求失败 [{endpoint}]: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"ES响应解析失败 [{endpoint}]: {e}")
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """获取集群基本信息"""
        try:
            info = self._make_request('/')
            return info
        except Exception as e:
            raise ConnectionError(f"无法获取集群信息: {e}")
    
    def get_cluster_health(self) -> Dict[str, Any]:
        """获取集群健康状态"""
        return self._make_request('/_cluster/health')
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """获取集群统计信息"""
        return self._make_request('/_cluster/stats')
    
    def get_nodes_info(self) -> Dict[str, Any]:
        """获取节点信息"""
        return self._make_request('/_nodes')
    
    def get_nodes_stats(self) -> Dict[str, Any]:
        """获取节点统计信息"""
        return self._make_request('/_nodes/stats')
    
    def get_indices_info(self) -> Dict[str, Any]:
        """获取索引信息"""
        return self._make_request('/_cat/indices?v&format=json&s=store.size:desc')
    
    def get_indices_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        return self._make_request('/_stats')
    
    def get_shards_info(self) -> List[Dict[str, Any]]:
        """获取分片信息"""
        return self._make_request('/_cat/shards?v&format=json')
    
    def get_allocation_info(self) -> List[Dict[str, Any]]:
        """获取分片分配信息"""
        return self._make_request('/_cat/allocation?v&format=json')
    
    def get_thread_pool_stats(self) -> Dict[str, Any]:
        """获取线程池统计"""
        return self._make_request('/_nodes/stats/thread_pool')
    
    def get_jvm_stats(self) -> Dict[str, Any]:
        """获取JVM统计信息"""
        return self._make_request('/_nodes/stats/jvm')
    
    def get_cluster_settings(self) -> Dict[str, Any]:
        """获取集群设置"""
        return self._make_request('/_cluster/settings')
    
    def inspect_cluster(self) -> Dict[str, Any]:
        """
        执行完整的集群检查
        
        Returns:
            包含所有检查结果的字典
        """
        print("🔍 开始ES集群巡检...")
        
        result = {
            'inspection_time': datetime.now().isoformat(),
            'cluster_info': {},
            'cluster_health': {},
            'cluster_stats': {},
            'nodes_info': {},
            'nodes_stats': {},
            'indices_info': [],
            'indices_stats': {},
            'shards_info': [],
            'allocation_info': [],
            'thread_pool_stats': {},
            'jvm_stats': {},
            'cluster_settings': {},
            'errors': []
        }
        
        # 依次收集各种信息
        checks = [
            ('cluster_info', self.get_cluster_info, "集群基本信息"),
            ('cluster_health', self.get_cluster_health, "集群健康状态"),
            ('cluster_stats', self.get_cluster_stats, "集群统计信息"),
            ('nodes_info', self.get_nodes_info, "节点信息"),
            ('nodes_stats', self.get_nodes_stats, "节点统计"),
            ('indices_info', self.get_indices_info, "索引信息"),
            ('indices_stats', self.get_indices_stats, "索引统计"),
            ('shards_info', self.get_shards_info, "分片信息"),
            ('allocation_info', self.get_allocation_info, "分片分配"),
            ('thread_pool_stats', self.get_thread_pool_stats, "线程池统计"),
            ('jvm_stats', self.get_jvm_stats, "JVM统计"),
            ('cluster_settings', self.get_cluster_settings, "集群设置"),
        ]
        
        for key, method, description in checks:
            try:
                print(f"  📊 收集{description}...")
                result[key] = method()
            except Exception as e:
                error_msg = f"收集{description}失败: {e}"
                print(f"  ❌ {error_msg}")
                result['errors'].append(error_msg)
        
        print(f"✅ 集群巡检完成，共收集 {len([k for k, v in result.items() if v and k != 'errors'])} 项信息")
        
        return result


def test_connection(config: Dict[str, Any]) -> bool:
    """测试ES连接"""
    try:
        inspector = ElasticsearchInspector(config)
        info = inspector.get_cluster_info()
        print(f"✅ 连接成功: {info.get('cluster_name', 'Unknown')} (版本: {info.get('version', {}).get('number', 'Unknown')})")
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    test_config = {
        'host': 'localhost',
        'port': 9200,
        'username': None,
        'password': None,
        'use_ssl': False,
        'verify_certs': False
    }
    
    if test_connection(test_config):
        inspector = ElasticsearchInspector(test_config)
        data = inspector.inspect_cluster()
        print(f"收集到的数据键: {list(data.keys())}") 