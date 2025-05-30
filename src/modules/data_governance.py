from typing import Dict, Any, List, Tuple
from datetime import datetime
from ..data_loader import ESDataLoader
import json
import os


class FinalRecommendationsGenerator:
    """最终建议生成器"""
    
    def __init__(self, data_loader: ESDataLoader):
        self.data_loader = data_loader
    
    def generate(self) -> str:
        """生成最终建议内容"""
        content = ""
        
        # 7.1 集群健康状况评估
        content += self._generate_health_assessment()
        
        # 7.2 需要业务确认的配置项
        content += self._generate_business_confirmation_items()
        
        # 7.3 优化建议
        content += self._generate_optimization_recommendations()
        
        return content
    
    def _generate_health_assessment(self) -> str:
        """生成集群健康状况评估"""
        content = """### 7.1 集群健康状况评估

"""
        
        # 获取基础健康数据
        cluster_health = self.data_loader.get_cluster_health()
        cluster_stats = self.data_loader.get_cluster_stats()
        nodes_stats = self.data_loader.get_nodes_stats()
        
        if not cluster_health:
            content += "无法获取集群健康状态信息\n\n"
            return content
        
        cluster_status = cluster_health.get('status', 'unknown')
        unassigned_shards = cluster_health.get('unassigned_shards', 0)
        relocating_shards = cluster_health.get('relocating_shards', 0)
        
        # 基础健康评估
        if cluster_status == 'green' and unassigned_shards == 0:
            content += """**整体评估**: ✅ 集群运行状态良好

**核心指标**:
- 集群状态: GREEN，所有分片正常分配
- 数据完整性: 100%，无数据丢失风险
- 服务可用性: 正常，可以稳定提供服务

"""
        elif cluster_status == 'yellow':
            content += """**整体评估**: 🟡 集群基本健康，存在副本分片问题

**核心指标**:
- 集群状态: YELLOW，主分片正常但副本分片有问题
- 数据完整性: 主分片完整，副本保护需要关注
- 服务可用性: 正常，但容错能力有所降低

"""
        else:
            content += """**整体评估**: 🔴 集群存在严重问题，需要立即处理

**核心指标**:
- 集群状态: RED，存在主分片问题
- 数据完整性: 部分数据可能无法访问
- 服务可用性: 受到影响，需要紧急处理

"""
        
        # 节点健康状况
        if nodes_stats:
            high_heap_nodes = []
            nodes = nodes_stats.get('nodes', {})
            
            for node_id, node_data in nodes.items():
                jvm_heap_percent = node_data.get('jvm', {}).get('mem', {}).get('heap_used_percent', 0)
                node_name = node_data.get('name', node_id)
                
                if jvm_heap_percent > 80:
                    high_heap_nodes.append((node_name, jvm_heap_percent))
            
            if high_heap_nodes:
                content += "**节点资源状况**: 🟡 部分节点堆内存使用率较高\n"
                for node_name, heap_percent in high_heap_nodes:
                    content += f"- {node_name}: {heap_percent:.1f}% 堆内存使用率\n"
                content += "\n"
            else:
                content += "**节点资源状况**: ✅ 所有节点资源使用正常\n\n"
        
        # 日志健康状况评估
        log_health_status = self._assess_log_health()
        content += f"**日志健康状况**: {log_health_status['status']} {log_health_status['description']}\n"
        if log_health_status['details']:
            for detail in log_health_status['details']:
                content += f"- {detail}\n"
        content += "\n"
        
        return content
    
    def _generate_business_confirmation_items(self) -> str:
        """生成需要业务确认的配置项"""
        content = """### 7.2 需要业务确认的配置项

以下配置项可能是业务场景的特殊需求，建议与相关业务人员确认是否为预期设置：

"""
        
        confirmation_items = []
        
        # 检查集群设置
        cluster_settings = self.data_loader.get_cluster_settings()
        if cluster_settings:
            persistent = cluster_settings.get('persistent', {})
            
            # 分片重平衡配置
            rebalance_enable = persistent.get('cluster', {}).get('routing', {}).get('rebalance', {}).get('enable')
            if rebalance_enable == 'none':
                confirmation_items.append({
                    'item': '分片重平衡已禁用',
                    'current': 'cluster.routing.rebalance.enable = none',
                    'reason': '可能是维护期间的临时设置或特殊业务需求',
                    'suggestion': '确认是否为临时设置，正常情况下建议启用'
                })
            
            # 分片分配配置
            allocation_enable = persistent.get('cluster', {}).get('routing', {}).get('allocation', {}).get('enable')
            if allocation_enable in ['none', 'primaries']:
                confirmation_items.append({
                    'item': '分片分配受限',
                    'current': f'cluster.routing.allocation.enable = {allocation_enable}',
                    'reason': '可能是维护操作或故障恢复过程中的设置',
                    'suggestion': '确认维护操作是否完成，可考虑恢复为正常分配'
                })
        
        # 检查大索引配置
        indices_stats = self.data_loader.get_indices_stats()
        if indices_stats:
            large_indices = []
            indices = indices_stats.get('indices', {})
            
            for index_name, index_data in indices.items():
                if index_name.startswith('.'):  # 跳过系统索引
                    continue
                    
                doc_count = index_data.get('total', {}).get('docs', {}).get('count', 0)
                if doc_count > 200_000_000:  # 超过2亿文档
                    size_bytes = index_data.get('total', {}).get('store', {}).get('size_in_bytes', 0)
                    large_indices.append((index_name, doc_count, size_bytes))
            
            if large_indices:
                confirmation_items.append({
                    'item': '超大索引存在',
                    'current': f'发现{len(large_indices)}个索引文档数超过2亿',
                    'reason': '可能是业务需求或历史数据积累',
                    'suggestion': '确认是否符合业务预期，可考虑按时间分割索引'
                })
        
        # 输出确认项
        if confirmation_items:
            for i, item in enumerate(confirmation_items, 1):
                content += f"""**{i}. {item['item']}**
- **当前状态**: {item['current']}
- **可能原因**: {item['reason']}
- **建议操作**: {item['suggestion']}

"""
        else:
            content += "✅ 未发现需要特别确认的配置项，当前配置基本符合常规运维标准。\n\n"
        
        return content
    
    def _generate_optimization_recommendations(self) -> str:
        """生成优化建议"""
        content = """### 7.3 优化建议

以下是基于当前集群状况提出的优化建议，按优先级排序：

"""
        
        recommendations = []
        
        # 分析索引优化机会
        indices_stats = self.data_loader.get_indices_stats()
        indices_settings = self.data_loader.get_settings()
        
        if indices_stats and indices_settings:
            # 检查分片优化机会
            oversized_shards = []
            undersized_shards = []
            
            for index_name, index_data in indices_stats.get('indices', {}).items():
                if index_name.startswith('.'):  # 跳过系统索引
                    continue
                
                # 获取分片数量
                index_config = indices_settings.get(index_name, {})
                if index_config:
                    index_settings = index_config.get('settings', {}).get('index', {})
                    shard_count = int(index_settings.get('number_of_shards', 1))
                    
                    # 计算单分片大小
                    total_size = index_data.get('total', {}).get('store', {}).get('size_in_bytes', 0)
                    if shard_count > 0:
                        shard_size_gb = total_size / shard_count / (1024**3)
                        
                        if shard_size_gb > 50:  # 超过50GB
                            oversized_shards.append((index_name, shard_size_gb, shard_count))
                        elif shard_size_gb < 1 and total_size > 100*1024*1024:  # 小于1GB但索引大于100MB
                            undersized_shards.append((index_name, shard_size_gb, shard_count))
            
            # 分片优化建议
            if oversized_shards:
                recommendations.append({
                    'priority': '中等',
                    'category': '分片优化',
                    'title': '大分片优化建议',
                    'description': f'发现{len(oversized_shards)}个索引的分片大小超过50GB',
                    'impact': '可提升索引操作性能和故障恢复速度',
                    'action': '考虑增加分片数量或使用时间分割策略',
                    'urgency': '可在业务低峰期进行调整'
                })
            
            if len(undersized_shards) >= 10:  # 超过10个小分片索引才建议优化
                recommendations.append({
                    'priority': '低',
                    'category': '分片整合',
                    'title': '小分片整合建议',
                    'description': f'发现{len(undersized_shards)}个索引分片偏小',
                    'impact': '可减少系统开销，提升整体性能',
                    'action': '考虑减少分片数量或合并小索引',
                    'urgency': '非紧急，可在系统维护时考虑'
                })
        
        # 检查ILM策略
        ilm_policies = self.data_loader.load_json_file('commercial/ilm_policies.json')
        if not ilm_policies:
            recommendations.append({
                'priority': '中等',
                'category': '生命周期管理',
                'title': 'ILM策略配置',
                'description': '当前未配置索引生命周期管理',
                'impact': '可自动管理索引生命周期，优化存储成本',
                'action': '根据业务需求配置ILM策略',
                'urgency': '建议结合业务需求逐步实施'
            })
        
        # 输出建议
        if recommendations:
            # 按优先级排序
            priority_order = {'高': 1, '中等': 2, '低': 3}
            recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
            
            for i, rec in enumerate(recommendations, 1):
                priority_icon = {'高': '🔴', '中等': '🟡', '低': '🟢'}.get(rec['priority'], '⚪')
                content += f"""**{i}. {rec['title']}** {priority_icon} {rec['priority']}优先级

- **现状描述**: {rec['description']}
- **预期收益**: {rec['impact']}
- **建议操作**: {rec['action']}
- **实施时机**: {rec['urgency']}

"""
        else:
            content += "✅ 当前集群配置已经比较优化，暂无明显的优化建议。\n\n"
        
        # 总结
        content += """**优化实施原则**:
- 优先处理影响稳定性和性能的问题
- 所有调整建议在业务低峰期进行
- 重要配置变更前请做好备份和回滚准备
- 定期监控调整效果，根据实际情况微调参数

"""
        
        return content
    
    def _assess_log_health(self) -> Dict[str, Any]:
        """评估日志健康状况"""
        logs_dir = os.path.join(self.data_loader.data_dir, 'logs')
        
        if not os.path.exists(logs_dir):
            return {
                'status': '⚠️',
                'description': '日志目录不存在，无法评估日志健康状况',
                'details': []
            }
        
        try:
            # 统计日志文件信息
            log_files = []
            total_size = 0
            current_log_size = 0
            compressed_count = 0
            
            for filename in os.listdir(logs_dir):
                if filename.endswith('.log') or filename.endswith('.log.gz'):
                    file_path = os.path.join(logs_dir, filename)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        if filename.endswith('.gz'):
                            compressed_count += 1
                        else:
                            current_log_size += file_size
                        
                        log_files.append({
                            'name': filename,
                            'size': file_size,
                            'compressed': filename.endswith('.gz')
                        })
            
            # 检查错误和警告
            has_errors = self._check_log_errors(logs_dir)
            has_warnings = self._check_log_warnings(logs_dir)
            
            # 评估健康状况
            status = "✅"
            description = "日志状况良好"
            details = []
            
            # 检查累积情况
            if len(log_files) > 50:
                status = "🔴"
                description = "日志累积过多，需要清理"
                details.append(f"日志文件数量({len(log_files)})过多，建议定期清理")
            elif len(log_files) > 20:
                status = "🟡"
                description = "日志累积较多，建议关注"
                details.append(f"日志文件数量({len(log_files)})较多，建议配置轮转策略")
            
            if total_size > 1024 * 1024 * 1024:  # 超过1GB
                status = "🔴"
                description = "日志大小过大，需要清理"
                details.append(f"日志总大小({self._format_log_size(total_size)})过大")
            elif total_size > 500 * 1024 * 1024:  # 超过500MB
                if status == "✅":
                    status = "🟡"
                    description = "日志大小适中，建议监控"
                details.append(f"日志大小({self._format_log_size(total_size)})需要关注增长趋势")
            
            # 检查错误和警告
            if has_errors:
                status = "🔴"
                description = "发现错误日志，需要处理"
                details.append("发现ERROR或FATAL级别的错误日志")
            
            if has_warnings:
                if status == "✅":
                    status = "🟡"
                    description = "发现警告日志，建议关注"
                details.append("发现WARN级别的警告日志")
            
            # 如果没有问题，补充健康详情
            if status == "✅":
                details = [
                    f"日志文件总数: {len(log_files)}个（包含{compressed_count}个压缩文件）",
                    f"总占用空间: {self._format_log_size(total_size)}",
                    "未发现错误或警告日志",
                    "日志累积情况正常"
                ]
            
            return {
                'status': status,
                'description': description,
                'details': details
            }
            
        except Exception as e:
            return {
                'status': '❌',
                'description': f'日志健康评估失败: {e}',
                'details': []
            }
    
    def _check_log_errors(self, logs_dir: str) -> bool:
        """检查是否存在错误日志"""
        try:
            for filename in os.listdir(logs_dir):
                if filename.endswith('.log'):  # 只检查未压缩的日志
                    file_path = os.path.join(logs_dir, filename)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if '[ERROR]' in line or '[FATAL]' in line:
                                return True
        except Exception:
            pass
        return False
    
    def _check_log_warnings(self, logs_dir: str) -> bool:
        """检查是否存在警告日志"""
        try:
            for filename in os.listdir(logs_dir):
                if filename.endswith('.log'):  # 只检查未压缩的日志
                    file_path = os.path.join(logs_dir, filename)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if '[WARN]' in line:
                                return True
        except Exception:
            pass
        return False
    
    def _format_log_size(self, size_bytes: int) -> str:
        """格式化日志文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def get_case_data(self) -> Dict[str, Any]:
        """获取用于检查的原始数据"""
        return {
            "cluster_health": self.data_loader.get_cluster_health(),
            "cluster_stats": self.data_loader.get_cluster_stats(),
            "cluster_settings": self.data_loader.get_cluster_settings(),
            "nodes_stats": self.data_loader.get_nodes_stats(),
            "indices_stats": self.data_loader.get_indices_stats(),
            "indices_settings": self.data_loader.get_settings(),
            "ilm_policies": self.data_loader.load_json_file('commercial/ilm_policies.json')
        } 