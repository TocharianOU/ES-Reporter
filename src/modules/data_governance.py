from typing import Dict, Any, List, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
from ..data_loader import ESDataLoader
import json
import os
from ..i18n import I18n


class FinalRecommendationsGenerator:
    """最终建议生成器"""
    
    def __init__(self, data_loader: ESDataLoader, language: str = "zh"):
        self.data_loader = data_loader
        self.language = language
        self.i18n = I18n(language)
    
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
        if self.language == 'en':
            content = """### 7.1 Cluster Health Assessment

"""
        else:
            content = """### 7.1 集群健康状况评估

"""
        
        # 获取基础健康数据
        cluster_health = self.data_loader.get_cluster_health()
        cluster_stats = self.data_loader.get_cluster_stats()
        nodes_stats = self.data_loader.get_nodes_stats()
        
        if not cluster_health:
            if self.language == 'en':
                content += "Unable to retrieve cluster health status information\n\n"
            else:
                content += "无法获取集群健康状态信息\n\n"
            return content
        
        cluster_status = cluster_health.get('status', 'unknown')
        unassigned_shards = cluster_health.get('unassigned_shards', 0)
        relocating_shards = cluster_health.get('relocating_shards', 0)
        
        # 基础健康评估
        if cluster_status == 'green' and unassigned_shards == 0:
            if self.language == 'en':
                content += """**Overall Assessment**: ✅ Cluster is running in good condition

**Core Indicators**:
- Cluster Status: GREEN, all shards properly allocated
- Data Integrity: 100%, no risk of data loss
- Service Availability: Normal, able to provide stable service

"""
            else:
                content += """**整体评估**: ✅ 集群运行状态良好

**核心指标**:
- 集群状态: GREEN，所有分片正常分配
- 数据完整性: 100%，无数据丢失风险
- 服务可用性: 正常，可以稳定提供服务

"""
        elif cluster_status == 'yellow':
            if self.language == 'en':
                content += """**Overall Assessment**: 🟡 Cluster is basically healthy with replica shard issues

**Core Indicators**:
- Cluster Status: YELLOW, primary shards normal but replica shards have issues
- Data Integrity: Primary shards intact, replica protection needs attention
- Service Availability: Normal, but fault tolerance is reduced

"""
            else:
                content += """**整体评估**: 🟡 集群基本健康，存在副本分片问题

**核心指标**:
- 集群状态: YELLOW，主分片正常但副本分片有问题
- 数据完整性: 主分片完整，副本保护需要关注
- 服务可用性: 正常，但容错能力有所降低

"""
        else:
            if self.language == 'en':
                content += """**Overall Assessment**: 🔴 Cluster has serious issues, requires immediate attention

**Core Indicators**:
- Cluster Status: RED, primary shard issues exist
- Data Integrity: Some data may be inaccessible
- Service Availability: Affected, requires urgent handling

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
                if self.language == 'en':
                    content += "**Node Resource Status**: 🟡 Some nodes have high heap memory usage\n"
                    for node_name, heap_percent in high_heap_nodes:
                        content += f"- {node_name}: {heap_percent:.1f}% heap memory usage\n"
                else:
                    content += "**节点资源状况**: 🟡 部分节点堆内存使用率较高\n"
                    for node_name, heap_percent in high_heap_nodes:
                        content += f"- {node_name}: {heap_percent:.1f}% 堆内存使用率\n"
                content += "\n"
            else:
                if self.language == 'en':
                    content += "**Node Resource Status**: ✅ All nodes have normal resource usage\n\n"
                else:
                    content += "**节点资源状况**: ✅ 所有节点资源使用正常\n\n"
        
        # 日志健康状况评估
        log_health_status = self._assess_log_health()
        if self.language == 'en':
            content += f"**Log Health Status**: {log_health_status['status']} {log_health_status['description']}\n"
        else:
            content += f"**日志健康状况**: {log_health_status['status']} {log_health_status['description']}\n"
        if log_health_status['details']:
            for detail in log_health_status['details']:
                content += f"- {detail}\n"
        content += "\n"
        
        return content
    
    def _generate_business_confirmation_items(self) -> str:
        """生成需要业务确认的配置项"""
        if self.language == 'en':
            content = """### 7.2 Items Requiring Business Confirmation

The following configuration items may be special requirements for business scenarios. It is recommended to confirm with relevant business personnel whether these are expected settings:

"""
        else:
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
                if self.language == 'en':
                    confirmation_items.append({
                        'item': 'Shard rebalancing disabled',
                        'current': 'cluster.routing.rebalance.enable = none',
                        'reason': 'May be a temporary setting during maintenance or special business requirement',
                        'suggestion': 'Confirm if this is a temporary setting, normally recommended to enable'
                    })
                else:
                    confirmation_items.append({
                        'item': '分片重平衡已禁用',
                        'current': 'cluster.routing.rebalance.enable = none',
                        'reason': '可能是维护期间的临时设置或特殊业务需求',
                        'suggestion': '确认是否为临时设置，正常情况下建议启用'
                    })
            
            # 分片分配配置
            allocation_enable = persistent.get('cluster', {}).get('routing', {}).get('allocation', {}).get('enable')
            if allocation_enable in ['none', 'primaries']:
                if self.language == 'en':
                    confirmation_items.append({
                        'item': 'Shard allocation restricted',
                        'current': f'cluster.routing.allocation.enable = {allocation_enable}',
                        'reason': 'May be a setting during maintenance operations or failure recovery',
                        'suggestion': 'Confirm if maintenance operations are complete, consider restoring to normal allocation'
                    })
                else:
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
                if self.language == 'en':
                    confirmation_items.append({
                        'item': 'Very large indices exist',
                        'current': f'Found {len(large_indices)} indices with over 200 million documents',
                        'reason': 'May be business requirements or historical data accumulation',
                        'suggestion': 'Confirm if this meets business expectations, consider splitting indices by time'
                    })
                else:
                    confirmation_items.append({
                        'item': '超大索引存在',
                        'current': f'发现{len(large_indices)}个索引文档数超过2亿',
                        'reason': '可能是业务需求或历史数据积累',
                        'suggestion': '确认是否符合业务预期，可考虑按时间分割索引'
                    })
        
        # 输出确认项
        if confirmation_items:
            for i, item in enumerate(confirmation_items, 1):
                if self.language == 'en':
                    content += f"""**{i}. {item['item']}**
- **Current Status**: {item['current']}
- **Possible Reason**: {item['reason']}
- **Recommended Action**: {item['suggestion']}

"""
                else:
                    content += f"""**{i}. {item['item']}**
- **当前状态**: {item['current']}
- **可能原因**: {item['reason']}
- **建议操作**: {item['suggestion']}

"""
        else:
            if self.language == 'en':
                content += "✅ No configuration items requiring special confirmation found. Current configuration generally meets standard operational practices.\n\n"
            else:
                content += "✅ 未发现需要特别确认的配置项，当前配置基本符合常规运维标准。\n\n"
        
        return content
    
    def _generate_optimization_recommendations(self) -> str:
        """生成优化建议"""
        if self.language == 'en':
            content = """### 7.3 Optimization Recommendations

The following optimization recommendations are based on current cluster conditions, sorted by priority:

"""
        else:
            content = """### 7.3 优化建议

以下是基于当前集群状况提出的优化建议，按优先级排序：

"""
        
        recommendations = []
        
        # 获取基础数据
        cluster_stats = self.data_loader.get_cluster_stats()
        nodes_stats = self.data_loader.get_nodes_stats()
        indices_stats = self.data_loader.get_indices_stats()
        
        # 堆内存优化建议
        if nodes_stats:
            high_heap_nodes = []
            nodes = nodes_stats.get('nodes', {})
            
            for node_id, node_data in nodes.items():
                jvm_heap_percent = node_data.get('jvm', {}).get('mem', {}).get('heap_used_percent', 0)
                node_name = node_data.get('name', node_id)
                if jvm_heap_percent > 80:
                    high_heap_nodes.append((node_name, jvm_heap_percent))
            
            if high_heap_nodes:
                if self.language == 'en':
                    recommendations.append({
                        'title': 'JVM Heap Memory Optimization',
                        'priority': 'High',
                        'description': f'Found {len(high_heap_nodes)} nodes with heap usage > 80%',
                        'action': 'Check for memory leaks, optimize queries, or increase heap size',
                        'impact': 'Can improve cluster stability and prevent OOM errors',
                        'urgency': 'Recommended to resolve within 1-2 days'
                    })
                else:
                    recommendations.append({
                        'title': 'JVM堆内存优化',
                        'priority': '高',
                        'description': f'发现{len(high_heap_nodes)}个节点堆内存使用率超过80%',
                        'action': '检查内存泄漏、优化查询语句或增加堆内存大小',
                        'impact': '可以提升集群稳定性，防止OOM错误',
                        'urgency': '建议1-2天内处理'
                    })
        
        # 分片优化建议
        if indices_stats:
            large_shards = []
            undersized_shards = []
            indices = indices_stats.get('indices', {})
            
            for index_name, index_data in indices.items():
                if index_name.startswith('.'):  # 跳过系统索引
                    continue
                
                # 获取主分片数和分片大小
                shards_stats = index_data.get('shards', {})
                primary_size = 0
                shard_count = 0
                
                for shard_id, shard_list in shards_stats.items():
                    for shard in shard_list:
                        if shard.get('routing', {}).get('primary', False):
                            shard_count += 1
                            shard_size_bytes = shard.get('store', {}).get('size_in_bytes', 0)
                            if shard_size_bytes > 50 * 1024 * 1024 * 1024:  # > 50GB
                                large_shards.append(index_name)
                            elif shard_size_bytes < 1 * 1024 * 1024 * 1024:  # < 1GB  
                                undersized_shards.append(index_name)
            
            if large_shards:
                if self.language == 'en':
                    recommendations.append({
                        'title': 'Large Shard Optimization',
                        'priority': 'Medium',
                        'description': f'Found {len(large_shards)} indices with shards > 50GB',
                        'action': 'Consider increasing primary shard count or implementing time-based splitting',
                        'impact': 'Can improve indexing performance and failure recovery speed',
                        'urgency': 'Recommended to implement gradually based on business requirements'
                    })
                else:
                    recommendations.append({
                        'title': '大分片优化建议',
                        'priority': '中等',
                        'description': f'发现{len(large_shards)}个索引存在超过50GB的分片',
                        'action': '考虑增加主分片数或实施按时间分割策略',
                        'impact': '可提升索引操作性能和故障恢复速度',
                        'urgency': '建议结合业务需求逐步实施'
                    })
            
            if len(undersized_shards) >= 10:  # 超过10个小分片索引才建议优化
                if self.language == 'en':
                    recommendations.append({
                        'title': 'Small Shard Consolidation',
                        'priority': 'Low',
                        'description': f'Found {len(undersized_shards)} indices with shards < 1GB',
                        'action': 'Consider consolidating related indices or reducing primary shard count',
                        'impact': 'Can reduce metadata overhead and improve cluster efficiency',
                        'urgency': 'Recommended to implement gradually based on business requirements'
                    })
                else:
                    recommendations.append({
                        'title': '小分片整合建议',
                        'priority': '低',
                        'description': f'发现{len(undersized_shards)}个索引存在小于1GB的分片',
                        'action': '考虑整合相关索引或减少主分片数',
                        'impact': '可以减少元数据开销，提升集群效率',
                        'urgency': '建议结合业务需求逐步实施'
                    })
        
        # 输出建议
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                if self.language == 'en':
                    priority_icon = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(rec['priority'], '⚪')
                    content += f"""**{i}. {rec['title']}** {priority_icon} {rec['priority']} Priority

- **Current Description**: {rec['description']}
- **Expected Impact**: {rec['impact']}
- **Recommended Action**: {rec['action']}
- **Implementation Timeline**: {rec['urgency']}

"""
                else:
                    priority_icon = {'高': '🔴', '中等': '🟡', '低': '🟢'}.get(rec['priority'], '⚪')
                    content += f"""**{i}. {rec['title']}** {priority_icon} {rec['priority']}优先级

- **现状描述**: {rec['description']}
- **预期效果**: {rec['impact']}
- **建议操作**: {rec['action']}
- **实施时间**: {rec['urgency']}

"""
        else:
            if self.language == 'en':
                content += "✅ Current cluster configuration is already well optimized, no obvious optimization recommendations.\n\n"
            else:
                content += "✅ 当前集群配置已经比较优化，暂无明显的优化建议。\n\n"
        
        # 通用注意事项
        if self.language == 'en':
            content += """**General Implementation Notes**:
- All optimization recommendations should be implemented during business low-peak hours
- Back up important data before making any configuration changes
- Implement changes gradually and monitor cluster performance
- Discuss implementation plans with business teams to ensure service continuity

"""
        else:
            content += """**通用实施说明**:
- 所有调整建议在业务低峰期进行
- 重要配置修改前请备份重要数据
- 分阶段实施并监控集群性能变化
- 与业务方沟通实施计划，确保服务连续性

"""
        
        return content
    
    def _assess_log_health(self) -> Dict[str, Any]:
        """评估日志健康状况"""
        logs_dir = os.path.join(self.data_loader.data_dir, 'logs')
        
        if not os.path.exists(logs_dir):
            if self.language == 'en':
                return {
                    'status': '⚠️',
                    'description': 'Log directory does not exist, unable to assess log health',
                    'details': []
                }
            else:
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
            if self.language == 'en':
                description = "Log status is good"
            else:
                description = "日志状况良好"
            details = []
            
            # 检查累积情况
            if len(log_files) > 50:
                status = "🔴"
                if self.language == 'en':
                    description = "Too many log files accumulated, cleanup needed"
                    details.append(f"Log file count ({len(log_files)}) is excessive, recommend regular cleanup")
                else:
                    description = "日志累积过多，需要清理"
                    details.append(f"日志文件数量({len(log_files)})过多，建议定期清理")
            elif len(log_files) > 20:
                status = "🟡"
                if self.language == 'en':
                    description = "Many log files accumulated, monitoring recommended"
                    details.append(f"Log file count ({len(log_files)}) is high, recommend configuring rotation strategy")
                else:
                    description = "日志累积较多，建议关注"
                    details.append(f"日志文件数量({len(log_files)})较多，建议配置轮转策略")
            
            if total_size > 1024 * 1024 * 1024:  # 超过1GB
                status = "🔴"
                if self.language == 'en':
                    description = "Log size too large, cleanup needed"
                    details.append(f"Total log size ({self._format_log_size(total_size)}) is excessive")
                else:
                    description = "日志大小过大，需要清理"
                    details.append(f"日志总大小({self._format_log_size(total_size)})过大")
            elif total_size > 500 * 1024 * 1024:  # 超过500MB
                if status == "✅":
                    status = "🟡"
                    if self.language == 'en':
                        description = "Log size moderate, monitoring recommended"
                    else:
                        description = "日志大小适中，建议监控"
                if self.language == 'en':
                    details.append(f"Log size ({self._format_log_size(total_size)}) needs attention for growth trend")
                else:
                    details.append(f"日志大小({self._format_log_size(total_size)})需要关注增长趋势")
            
            # 检查错误和警告
            if has_errors:
                status = "🔴"
                if self.language == 'en':
                    description = "Error logs found, handling required"
                    details.append("Found ERROR or FATAL level error logs")
                else:
                    description = "发现错误日志，需要处理"
                    details.append("发现ERROR或FATAL级别的错误日志")
            
            if has_warnings:
                if status == "✅":
                    status = "🟡"
                    if self.language == 'en':
                        description = "Warning logs found, attention recommended"
                    else:
                        description = "发现警告日志，建议关注"
                if self.language == 'en':
                    details.append("Found WARN level warning logs")
                else:
                    details.append("发现WARN级别的警告日志")
            
            # 如果没有问题，补充健康详情
            if status == "✅":
                if self.language == 'en':
                    details = [
                        f"Total log files: {len(log_files)} (including {compressed_count} compressed files)",
                        f"Total space used: {self._format_log_size(total_size)}",
                        "No error or warning logs found",
                        "Log accumulation status is normal"
                    ]
                else:
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
            if self.language == 'en':
                return {
                    'status': '❌',
                    'description': f'Log health assessment failed: {e}',
                    'details': []
                }
            else:
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