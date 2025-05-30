from typing import Dict, Any, List
from datetime import datetime
from ..data_loader import ESDataLoader
from ..i18n import I18n


class ClusterBasicInfoGenerator:
    """集群基础信息生成器"""
    
    def __init__(self, data_loader: ESDataLoader, language: str = "zh"):
        self.data_loader = data_loader
        self.language = language
        self.i18n = I18n(language)
    
    def generate(self) -> str:
        """生成集群基础信息内容"""
        cluster_stats = self.data_loader.get_cluster_stats()
        cluster_health = self.data_loader.get_cluster_health()
        master_info = self.data_loader.load_json_file('master.json')
        nodes_info = self.data_loader.get_nodes()
        cluster_settings = self.data_loader.load_json_file('cluster_settings.json')
        
        content = ""
        
        # 3.1 集群标识信息
        content += self._generate_cluster_identity(cluster_stats, cluster_health)
        
        # 3.2 主节点信息
        content += self._generate_master_info(master_info, nodes_info)
        
        # 3.3 集群拓扑结构
        content += self._generate_topology_info(cluster_stats, nodes_info)
        
        # 3.4 集群设置概览
        content += self._generate_settings_overview(cluster_settings, nodes_info)
        
        # 3.5 集群状态统计
        content += self._generate_status_statistics(cluster_stats, cluster_health)
        
        # 3.6 存储架构
        content += self._generate_storage_architecture(cluster_stats)
        
        # 3.7 分片分布策略
        content += self._generate_shard_strategy(cluster_settings, cluster_stats)
        
        return content
    
    def _generate_cluster_identity(self, cluster_stats: Dict, cluster_health: Dict) -> str:
        """生成集群标识信息"""
        cluster_uuid = "N/A"
        cluster_name = "N/A"
        cluster_status = "N/A"
        
        if cluster_stats:
            cluster_uuid = cluster_stats.get('cluster_uuid', 'N/A')
            cluster_name = cluster_stats.get('cluster_name', 'N/A')
            cluster_status = cluster_stats.get('status', 'N/A')
        elif cluster_health:
            cluster_name = cluster_health.get('cluster_name', 'N/A')
            cluster_status = cluster_health.get('status', 'N/A')
        
        if self.language == 'en':
            return f"""### 3.1 Cluster Identity Information

| Item | Value |
|------|-------|
| **Cluster UUID** | `{cluster_uuid}` |
| **Cluster Name** | `{cluster_name}` |
| **Cluster Status** | `{cluster_status.upper()}` |
| **Cluster Description** | Production Environment Cluster |

"""
        else:
            return f"""### 3.1 集群标识信息

| 项目 | 值 |
|------|------|
| **集群UUID** | `{cluster_uuid}` |
| **集群名称** | `{cluster_name}` |
| **集群状态** | `{cluster_status.upper()}` |
| **集群描述** | 生产环境集群 |

"""
    
    def _generate_master_info(self, master_info: List, nodes_info: Dict) -> str:
        """生成主节点信息"""
        if self.language == 'en':
            master_content = """### 3.2 Master Node Information

"""
        else:
            master_content = """### 3.2 主节点信息

"""
        
        if not master_info or not isinstance(master_info, list) or len(master_info) == 0:
            if self.language == 'en':
                master_content += "⚠️ **Warning**: Unable to retrieve master node information\n\n"
            else:
                master_content += "⚠️ **警告**: 无法获取主节点信息\n\n"
            return master_content
        
        master = master_info[0]
        master_id = master.get('id', 'N/A')
        master_name = master.get('node', 'N/A')
        master_host = master.get('host', 'N/A')
        master_ip = master.get('ip', 'N/A')
        
        # 从nodes_info中获取更多主节点详细信息
        master_roles = "N/A"
        master_version = "N/A"
        
        if nodes_info and 'nodes' in nodes_info:
            for node_id, node_data in nodes_info['nodes'].items():
                if node_id == master_id or node_data.get('name') == master_name:
                    master_roles = ", ".join(node_data.get('roles', []))
                    master_version = node_data.get('version', 'N/A')
                    break
        
        if self.language == 'en':
            master_content += f"""| Item | Value |
|------|-------|
| **Current Master Node** | `{master_name}` |
| **Node ID** | `{master_id}` |
| **Master Node Address** | `{master_host}:{master_ip}` |
| **Node Roles** | `{master_roles}` |
| **ES Version** | `{master_version}` |
| **Master Node Status** | Active |

"""
        else:
            master_content += f"""| 项目 | 值 |
|------|------|
| **当前主节点** | `{master_name}` |
| **节点ID** | `{master_id}` |
| **主节点地址** | `{master_host}:{master_ip}` |
| **节点角色** | `{master_roles}` |
| **ES版本** | `{master_version}` |
| **主节点状态** | 活跃 |

"""
        return master_content
    
    def _generate_topology_info(self, cluster_stats: Dict, nodes_info: Dict) -> str:
        """生成集群拓扑结构信息"""
        if self.language == 'en':
            content = """### 3.3 Cluster Topology

"""
        else:
            content = """### 3.3 集群拓扑结构

"""
        
        # 节点总览
        total_nodes = "N/A"
        successful_nodes = "N/A"
        
        if cluster_stats and '_nodes' in cluster_stats:
            total_nodes = cluster_stats['_nodes'].get('total', 'N/A')
            successful_nodes = cluster_stats['_nodes'].get('successful', 'N/A')
        
        if self.language == 'en':
            content += f"""#### 3.3.1 Node Overview

| Item | Count |
|------|-------|
| **Total Nodes** | {total_nodes} |
| **Responding Nodes** | {successful_nodes} |

"""
        else:
            content += f"""#### 3.3.1 节点总览

| 项目 | 数量 |
|------|------|
| **节点总数** | {total_nodes} |
| **响应节点数** | {successful_nodes} |

"""
        
        # 分析节点角色分布
        if nodes_info and 'nodes' in nodes_info:
            role_stats = self._analyze_node_roles(nodes_info['nodes'])
            
            if self.language == 'en':
                content += """#### 3.3.2 Node Role Distribution

| Role Type | Count | Node List |
|-----------|-------|-----------|
"""
            else:
                content += """#### 3.3.2 节点角色分布

| 角色类型 | 数量 | 节点列表 |
|---------|------|----------|
"""
            
            for role, info in role_stats.items():
                nodes_list = ", ".join(info['nodes'][:5])  # 最多显示5个节点
                if len(info['nodes']) > 5:
                    if self.language == 'en':
                        nodes_list += f", ... (total {len(info['nodes'])} nodes)"
                    else:
                        nodes_list += f", ... (共{len(info['nodes'])}个)"
                content += f"| **{role}** | {info['count']} | {nodes_list} |\n"
            
            content += "\n"
            
            # IP地址分布
            ip_distribution = self._analyze_ip_distribution(nodes_info['nodes'])
            
            if self.language == 'en':
                content += f"""#### 3.3.3 Network Distribution

- **IP Address Segment Distribution**: 
"""
                for ip_segment, count in ip_distribution.items():
                    content += f"  - `{ip_segment}`: {count} nodes\n"
            else:
                content += f"""#### 3.3.3 网络分布

- **IP地址段分布**: 
"""
                for ip_segment, count in ip_distribution.items():
                    content += f"  - `{ip_segment}`: {count} 个节点\n"
            
            content += "\n"
        
        return content
    
    def _generate_settings_overview(self, cluster_settings: Dict, nodes_info: Dict) -> str:
        """生成集群设置概览"""
        if self.language == 'en':
            content = """### 3.4 Cluster Settings Overview

"""
        else:
            content = """### 3.4 集群设置概览

"""
        
        # 关键配置参数
        if self.language == 'en':
            content += """#### 3.4.1 Key Configuration Parameters

"""
        else:
            content += """#### 3.4.1 关键配置参数

"""
        
        # 从节点信息中获取设置信息
        if nodes_info and 'nodes' in nodes_info:
            # 取第一个节点的设置作为示例
            first_node = next(iter(nodes_info['nodes'].values()))
            settings = first_node.get('settings', {})
            
            cluster_name = settings.get('cluster', {}).get('name', 'N/A')
            http_port = settings.get('http', {}).get('port', 'N/A')
            transport_port = settings.get('transport', {}).get('port', 'N/A')
            network_host = settings.get('network', {}).get('host', 'N/A')
            discovery_type = "zen" if 'discovery' in settings else 'N/A'
            
            if self.language == 'en':
                content += f"""| Configuration Item | Value |
|-------------------|-------|
| **cluster.name** | `{cluster_name}` |
| **network.host** | `{network_host}` |
| **http.port** | `{http_port}` |
| **transport.port** | `{transport_port}` |
| **Discovery Mechanism** | `{discovery_type}` |

"""
            else:
                content += f"""| 配置项 | 值 |
|--------|------|
| **cluster.name** | `{cluster_name}` |
| **network.host** | `{network_host}` |
| **http.port** | `{http_port}` |
| **transport.port** | `{transport_port}` |
| **发现机制** | `{discovery_type}` |

"""
        
        # 动态设置
        if cluster_settings:
            if self.language == 'en':
                content += """#### 3.4.2 Dynamic Configuration

"""
            else:
                content += """#### 3.4.2 动态配置

"""
            
            persistent = cluster_settings.get('persistent', {})
            transient = cluster_settings.get('transient', {})
            
            if persistent:
                if self.language == 'en':
                    content += "**Persistent Settings**:\n"
                else:
                    content += "**持久化设置**:\n"
                for key, value in persistent.items():
                    content += f"- `{key}`: `{value}`\n"
                content += "\n"
            
            if transient:
                if self.language == 'en':
                    content += "**Transient Settings**:\n"
                else:
                    content += "**临时设置**:\n"
                for key, value in transient.items():
                    content += f"- `{key}`: `{value}`\n"
                content += "\n"
            
            if not persistent and not transient:
                if self.language == 'en':
                    content += "- No dynamic configurations\n\n"
                else:
                    content += "- 暂无动态配置\n\n"
        
        return content
    
    def _generate_status_statistics(self, cluster_stats: Dict, cluster_health: Dict) -> str:
        """生成集群状态统计"""
        if self.language == 'en':
            content = """### 3.5 Cluster Status Statistics

"""
        else:
            content = """### 3.5 集群状态统计

"""
        
        # 任务队列状态
        pending_tasks = "N/A"
        max_waiting_time = "N/A"
        
        if cluster_health:
            pending_tasks = cluster_health.get('number_of_pending_tasks', 'N/A')
            max_waiting_time = cluster_health.get('task_max_waiting_in_queue_millis', 'N/A')
            if max_waiting_time != "N/A":
                max_waiting_time = f"{max_waiting_time} ms"
        
        # 集群时间戳
        cluster_timestamp = "N/A"
        if cluster_stats and 'timestamp' in cluster_stats:
            timestamp_ms = cluster_stats['timestamp']
            cluster_timestamp = self.data_loader.format_timestamp(timestamp_ms)
        
        if self.language == 'en':
            content += f"""| Item | Value |
|------|-------|
| **Data Collection Time** | {cluster_timestamp} |
| **Pending Tasks** | {pending_tasks} |
| **Max Waiting Time** | {max_waiting_time} |

"""
        else:
            content += f"""| 项目 | 值 |
|------|------|
| **数据收集时间** | {cluster_timestamp} |
| **待处理任务数** | {pending_tasks} |
| **最长等待时间** | {max_waiting_time} |

"""
        
        return content
    
    def _generate_storage_architecture(self, cluster_stats: Dict) -> str:
        """生成存储架构信息"""
        if self.language == 'en':
            content = """### 3.6 Storage Architecture

"""
        else:
            content = """### 3.6 存储架构

"""
        
        if cluster_stats and 'indices' in cluster_stats:
            indices = cluster_stats['indices']
            store_info = indices.get('store', {})
            
            total_size = store_info.get('size', 'N/A')
            size_bytes = store_info.get('size_in_bytes', 0)
            
            # 计算平均每节点存储
            total_nodes = cluster_stats.get('_nodes', {}).get('total', 1)
            avg_per_node = "N/A"
            if size_bytes and total_nodes:
                avg_per_node_bytes = size_bytes / total_nodes
                avg_per_node = self.data_loader.format_bytes(avg_per_node_bytes)
            
            if self.language == 'en':
                content += f"""| Item | Value |
|------|-------|
| **Total Storage Capacity** | {total_size} |
| **Storage Bytes** | {size_bytes:,} bytes |
| **Average Per Node Storage** | {avg_per_node} |

"""
            else:
                content += f"""| 项目 | 值 |
|------|------|
| **总存储容量** | {total_size} |
| **存储字节数** | {size_bytes:,} bytes |
| **平均节点存储** | {avg_per_node} |

"""
        
        return content
    
    def _generate_shard_strategy(self, cluster_settings: Dict, cluster_stats: Dict) -> str:
        """生成分片分布策略"""
        if self.language == 'en':
            content = """### 3.7 Shard Distribution Strategy

"""
        else:
            content = """### 3.7 分片分布策略

"""
        
        # 从cluster_stats获取分片信息
        if cluster_stats and 'indices' in cluster_stats:
            shards_info = cluster_stats['indices'].get('shards', {})
            
            total_shards = shards_info.get('total', 'N/A')
            primary_shards = shards_info.get('primaries', 'N/A')
            replication_factor = shards_info.get('replication', 'N/A')
            
            if self.language == 'en':
                content += f"""| Item | Value |
|------|-------|
| **Total Shards** | {total_shards} |
| **Primary Shards** | {primary_shards} |
| **Replication Factor** | {replication_factor} |

"""
            else:
                content += f"""| 项目 | 值 |
|------|------|
| **总分片数** | {total_shards} |
| **主分片数** | {primary_shards} |
| **副本系数** | {replication_factor} |

"""
        
        # 分片分配策略 - 根据实际设置动态生成描述
        if self.language == 'en':
            content += """#### Shard Allocation Settings

"""
        else:
            content += """#### 分片分配设置

"""
        
        if cluster_settings:
            persistent = cluster_settings.get('persistent', {})
            rebalance_setting = persistent.get('cluster.routing.rebalance.enable', 'all')
            
            if self.language == 'en':
                content += f"- **Rebalance Strategy**: `{rebalance_setting}`\n"
            else:
                content += f"- **重平衡策略**: `{rebalance_setting}`\n"
            
            # 根据不同的重平衡设置提供相应的说明
            if rebalance_setting == 'none':
                if self.language == 'en':
                    content += """- **Current Status**: ⚠️ **Shard rebalancing is disabled**
- **Impact Description**: 
  - Cluster will not automatically move shards to optimize distribution
  - Shards will not be automatically reallocated when nodes are added or removed
  - May cause load imbalance between nodes
- **Use Cases**: 
  - Prevent shard migration during maintenance
  - Avoid unnecessary network and disk IO
  - Maintain cluster stability
- **Recommendation**: Confirm if this is a temporary setting, recommend restoring to `all` after maintenance

"""
                else:
                    content += """- **当前状态**: ⚠️ **分片重平衡已被禁用**
- **影响说明**: 
  - 集群不会自动移动分片来优化分布
  - 新增或移除节点时分片不会自动重新分配
  - 可能导致节点间负载不均衡
- **使用场景**: 
  - 维护期间防止分片迁移
  - 避免不必要的网络和磁盘IO
  - 保持集群稳定性
- **建议**: 确认是否为临时设置，完成维护后建议恢复为 `all`

"""
            elif rebalance_setting == 'primaries':
                if self.language == 'en':
                    content += """- **Current Status**: Only primary shard rebalancing allowed
- **Impact Description**: 
  - Only primary shards participate in automatic reallocation
  - Replica shards maintain current distribution
- **Allocation Strategy**: Based on available space and load balancing of primary shards

"""
                else:
                    content += """- **当前状态**: 仅允许主分片重平衡
- **影响说明**: 
  - 只有主分片会参与自动重新分配
  - 副本分片保持当前分布不变
- **分配策略**: 基于主分片的可用空间和负载平衡

"""
            elif rebalance_setting == 'replicas':
                if self.language == 'en':
                    content += """- **Current Status**: Only replica shard rebalancing allowed
- **Impact Description**: 
  - Only replica shards participate in automatic reallocation
  - Primary shards maintain current distribution
- **Allocation Strategy**: Based on available space and load balancing of replica shards

"""
                else:
                    content += """- **当前状态**: 仅允许副本分片重平衡
- **影响说明**: 
  - 只有副本分片会参与自动重新分配
  - 主分片保持当前分布不变
- **分配策略**: 基于副本分片的可用空间和负载平衡

"""
            else:  # 'all' 或其他值
                if self.language == 'en':
                    content += """- **Current Status**: All shard rebalancing allowed (default)
- **Allocation Strategy**: 
  - Based on available space and shard count balancing
  - Both primary and replica shards participate in automatic reallocation
  - Cluster automatically optimizes shard distribution

"""
                else:
                    content += """- **当前状态**: 允许所有分片重平衡 (默认)
- **分配策略**: 
  - 基于可用空间和分片数量平衡
  - 主分片和副本分片都参与自动重新分配
  - 集群会自动优化分片分布

"""
        else:
            if self.language == 'en':
                content += """- **Rebalance Strategy**: `all` (default setting)
- **Allocation Strategy**: Based on available space and shard count balancing

"""
            else:
                content += """- **重平衡策略**: `all` (默认设置)
- **分配策略**: 基于可用空间和分片数量平衡

"""
        
        return content
    
    def _analyze_node_roles(self, nodes: Dict) -> Dict[str, Dict]:
        """分析节点角色分布"""
        role_stats = {}
        
        for node_id, node_data in nodes.items():
            node_name = node_data.get('name', node_id)
            roles = node_data.get('roles', [])
            
            for role in roles:
                if role not in role_stats:
                    role_stats[role] = {'count': 0, 'nodes': []}
                role_stats[role]['count'] += 1
                role_stats[role]['nodes'].append(node_name)
        
        return role_stats
    
    def _analyze_ip_distribution(self, nodes: Dict) -> Dict[str, int]:
        """分析IP地址分布"""
        ip_segments = {}
        
        for node_data in nodes.values():
            ip = node_data.get('ip', '')
            if ip:
                # 获取IP的前三段作为网段
                segments = ip.split('.')
                if len(segments) >= 3:
                    segment = '.'.join(segments[:3]) + '.x'
                    ip_segments[segment] = ip_segments.get(segment, 0) + 1
        
        return ip_segments
    
    def get_case_data(self) -> Dict[str, Any]:
        """获取用于检查的原始数据"""
        return {
            "cluster_stats": self.data_loader.get_cluster_stats(),
            "cluster_health": self.data_loader.get_cluster_health(),
            "master_info": self.data_loader.load_json_file('master.json'),
            "nodes_info": self.data_loader.get_nodes(),
            "cluster_settings": self.data_loader.load_json_file('cluster_settings.json')
        } 