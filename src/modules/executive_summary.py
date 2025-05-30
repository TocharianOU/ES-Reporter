from typing import Dict, Any
from ..data_loader import ESDataLoader


class ExecutiveSummaryGenerator:
    """执行摘要生成器"""
    
    def __init__(self, data_loader: ESDataLoader):
        self.data_loader = data_loader
    
    def generate(self) -> str:
        """生成执行摘要内容"""
        cluster_health = self.data_loader.get_cluster_health()
        cluster_stats = self.data_loader.get_cluster_stats()
        
        # 获取集群状态
        status = "unknown"
        status_icon = "❓"
        status_desc = "未知状态"
        
        if cluster_health:
            status = cluster_health.get('status', 'unknown').lower()
            if status == 'green':
                status_icon = "🟢"
                status_desc = "Green: 集群健康，所有分片正常"
            elif status == 'yellow':
                status_icon = "🟡" 
                status_desc = "Yellow: 存在未分配的副本分片"
            elif status == 'red':
                status_icon = "🔴"
                status_desc = "Red: 存在未分配的主分片"
        
        # 获取关键指标
        total_nodes = cluster_health.get('number_of_nodes', 'N/A') if cluster_health else 'N/A'
        data_nodes = cluster_health.get('number_of_data_nodes', 'N/A') if cluster_health else 'N/A'
        primary_shards = cluster_health.get('active_primary_shards', 'N/A') if cluster_health else 'N/A'
        total_shards = cluster_health.get('active_shards', 'N/A') if cluster_health else 'N/A'
        
        # 从cluster_stats获取索引和存储信息
        index_count = 'N/A'
        total_size = 'N/A'
        doc_count = 'N/A'
        
        if cluster_stats and 'indices' in cluster_stats:
            indices_info = cluster_stats['indices']
            index_count = indices_info.get('count', 'N/A')
            
            # 获取存储大小
            if 'store' in indices_info and 'size_in_bytes' in indices_info['store']:
                size_bytes = indices_info['store']['size_in_bytes']
                total_size = self.data_loader.format_bytes(size_bytes)
            
            # 获取文档数量
            if 'docs' in indices_info and 'count' in indices_info['docs']:
                doc_count = f"{indices_info['docs']['count']:,}"
        
        # 生成内容
        summary_content = f"""### 2.1 总体评估
- **集群状态**: {status.upper()}
  - {status_icon} {status_desc}

### 2.2 关键指标概览
- **节点总数**: {total_nodes} 个
- **数据节点数**: {data_nodes} 个
- **索引总数**: {index_count} 个
- **主分片数**: {primary_shards} 个
- **总分片数**: {total_shards} 个
- **数据总量**: {total_size}
- **文档总数**: {doc_count} 个

### 2.3 健康状态详情"""

        # 添加健康状态详情
        if cluster_health:
            relocating_shards = cluster_health.get('relocating_shards', 0)
            initializing_shards = cluster_health.get('initializing_shards', 0)
            unassigned_shards = cluster_health.get('unassigned_shards', 0)
            active_shards_percent = cluster_health.get('active_shards_percent_as_number', 0)
            
            summary_content += f"""
- **分片健康状态**:
  - 活跃分片百分比: {active_shards_percent}%
  - 重新分配中的分片: {relocating_shards}
  - 初始化中的分片: {initializing_shards}
  - 未分配的分片: {unassigned_shards}"""
            
            if unassigned_shards > 0:
                summary_content += f"\n  - ⚠️ **注意**: 存在 {unassigned_shards} 个未分配分片，需要关注"
            
            if relocating_shards > 0:
                summary_content += f"\n  - ℹ️ **信息**: 有 {relocating_shards} 个分片正在重新分配"

        return summary_content
    
    def get_case_data(self) -> Dict[str, Any]:
        """获取用于检查的原始数据"""
        return {
            "cluster_health": self.data_loader.get_cluster_health(),
            "cluster_stats": self.data_loader.get_cluster_stats()
        } 