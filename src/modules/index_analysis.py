from typing import Dict, Any, List, Tuple
from datetime import datetime
from ..data_loader import ESDataLoader
import re


class IndexAnalysisGenerator:
    """索引分析生成器"""
    
    def __init__(self, data_loader: ESDataLoader):
        self.data_loader = data_loader
    
    def generate(self) -> str:
        """生成索引分析内容"""
        content = ""
        
        # 5.1 索引概览统计
        content += self._generate_index_overview()
        
        # 5.2 索引详细信息表
        content += self._generate_index_details_table()
        
        # 5.3 索引健康状态分析
        content += self._generate_index_health_analysis()
        
        # 5.4 索引模式与分布
        content += self._generate_index_patterns_distribution()
        
        # 5.5 分片分布分析
        content += self._generate_shard_distribution_analysis()
        
        # 5.6 索引性能指标
        content += self._generate_index_performance_metrics()
        
        # 5.7 索引优化建议
        content += self._generate_index_optimization_recommendations()
        
        return content
    
    def _generate_index_overview(self) -> str:
        """生成索引概览统计"""
        content = """### 5.1 索引概览统计

"""
        
        cluster_stats = self.data_loader.get_cluster_stats()
        cluster_health = self.data_loader.get_cluster_health()
        
        if not cluster_stats or 'indices' not in cluster_stats:
            content += "❌ **无法获取索引统计信息**\n\n"
            return content
        
        indices_stats = cluster_stats['indices']
        
        # 基本统计
        total_indices = indices_stats.get('count', 0)
        total_shards = indices_stats.get('shards', {}).get('total', 0)
        primary_shards = indices_stats.get('shards', {}).get('primaries', 0)
        replica_shards = total_shards - primary_shards
        replication_factor = indices_stats.get('shards', {}).get('replication', 0)
        
        total_docs = indices_stats.get('docs', {}).get('count', 0)
        deleted_docs = indices_stats.get('docs', {}).get('deleted', 0)
        
        total_size = indices_stats.get('store', {}).get('size', 'N/A')
        total_size_bytes = indices_stats.get('store', {}).get('size_in_bytes', 0)
        
        content += f"""#### 5.1.1 基础统计信息

| 指标项 | 数值 | 说明 |
|--------|------|------|
| **索引总数** | {total_indices} | 集群中的索引数量 |
| **分片总数** | {total_shards} | 主分片 + 副本分片 |
| **主分片数** | {primary_shards} | 数据分片数量 |
| **副本分片数** | {replica_shards} | 冗余备份分片数量 |
| **副本因子** | {replication_factor:.1f} | 平均每个主分片的副本数 |
| **文档总数** | {total_docs:,} | 所有索引的文档总数 |
| **已删除文档** | {deleted_docs:,} | 标记为删除的文档数 |
| **数据总大小** | {total_size} | 所有索引占用存储空间 |

"""
        
        # 平均统计
        avg_shards_per_index = indices_stats.get('shards', {}).get('index', {}).get('shards', {}).get('avg', 0)
        avg_primaries_per_index = indices_stats.get('shards', {}).get('index', {}).get('primaries', {}).get('avg', 0)
        
        if total_indices > 0:
            avg_docs_per_index = total_docs // total_indices
            avg_size_per_index = total_size_bytes // total_indices if total_size_bytes > 0 else 0
            avg_size_per_index_str = self.data_loader.format_bytes(avg_size_per_index)
        else:
            avg_docs_per_index = 0
            avg_size_per_index_str = "0B"
        
        content += f"""#### 5.1.2 平均分布统计

| 指标项 | 数值 | 说明 |
|--------|------|------|
| **平均分片数/索引** | {avg_shards_per_index:.1f} | 每个索引的平均分片数 |
| **平均主分片数/索引** | {avg_primaries_per_index:.1f} | 每个索引的平均主分片数 |
| **平均文档数/索引** | {avg_docs_per_index:,} | 每个索引的平均文档数 |
| **平均大小/索引** | {avg_size_per_index_str} | 每个索引的平均存储大小 |

"""
        
        # 健康状态统计
        if cluster_health:
            active_primary_shards = cluster_health.get('active_primary_shards', 0)
            active_shards = cluster_health.get('active_shards', 0)
            relocating_shards = cluster_health.get('relocating_shards', 0)
            initializing_shards = cluster_health.get('initializing_shards', 0)
            unassigned_shards = cluster_health.get('unassigned_shards', 0)
            
            content += f"""#### 5.1.3 分片健康状态

| 状态类型 | 数量 | 百分比 | 说明 |
|----------|------|--------|------|
| **活跃分片** | {active_shards} | {(active_shards/total_shards*100):.1f}% | 正常工作的分片 |
| **活跃主分片** | {active_primary_shards} | {(active_primary_shards/primary_shards*100):.1f}% | 正常工作的主分片 |
| **迁移中分片** | {relocating_shards} | {(relocating_shards/total_shards*100):.1f}% | 正在节点间迁移的分片 |
| **初始化分片** | {initializing_shards} | {(initializing_shards/total_shards*100):.1f}% | 正在初始化的分片 |
| **未分配分片** | {unassigned_shards} | {(unassigned_shards/total_shards*100):.1f}% | 未能分配到节点的分片 |

"""
        
        return content
    
    def _generate_index_details_table(self) -> str:
        """生成索引详细信息表"""
        content = """### 5.2 索引详细信息表

#### 5.2.1 典型索引信息（20个代表性索引）

| 索引名称 | 状态 | 主分片数 | 副本数 | 文档数量 | 索引大小 | 类型说明 |
|----------|------|----------|--------|----------|----------|----------|
"""
        
        # 从分片数据中解析索引信息
        indices_data = self.data_loader.load_json_file('indices.json')
        if not indices_data:
            content += "| N/A | N/A | N/A | N/A | N/A | N/A | N/A |\n\n"
            return content
        
        # 解析索引信息
        index_info = {}
        for shard in indices_data:
            index_name = shard.get('index', 'unknown')
            if index_name not in index_info:
                index_info[index_name] = {
                    'primary_shards': 0,
                    'replica_shards': 0,
                    'docs': 0,
                    'store_bytes': 0,
                    'status': 'UNKNOWN'
                }
            
            if shard.get('prirep') == 'p':  # primary
                index_info[index_name]['primary_shards'] += 1
            else:  # replica
                index_info[index_name]['replica_shards'] += 1
            
            # 累计文档数和存储大小（只计算主分片，避免重复）
            if shard.get('prirep') == 'p':
                docs = shard.get('docs')
                store = shard.get('store')
                if docs and docs.isdigit():
                    index_info[index_name]['docs'] += int(docs)
                if store and store.isdigit():
                    index_info[index_name]['store_bytes'] += int(store)
            
            index_info[index_name]['status'] = shard.get('state', 'UNKNOWN')
        
        # 选择典型索引
        typical_indices = self._select_typical_indices(index_info)
        
        for index_name, info, type_desc in typical_indices:
            replicas = info['replica_shards'] // max(info['primary_shards'], 1) if info['primary_shards'] > 0 else 0
            docs_formatted = f"{info['docs']:,}" if info['docs'] > 0 else "0"
            size_formatted = self.data_loader.format_bytes(info['store_bytes'])
            
            # 简化索引名显示
            display_name = index_name[:25] + "..." if len(index_name) > 25 else index_name
            
            status_icon = "🟢" if info['status'] == 'STARTED' else "🔴"
            
            content += f"| {display_name} | {status_icon} | {info['primary_shards']} | {replicas} | {docs_formatted} | {size_formatted} | {type_desc} |\n"
        
        content += "\n"
        return content
    
    def _select_typical_indices(self, index_info: Dict) -> List[Tuple[str, Dict, str]]:
        """选择典型的索引进行展示（排除系统索引）"""
        typical_indices = []
        
        # 过滤掉系统索引，只保留应用索引
        app_index_info = {k: v for k, v in index_info.items() if not k.startswith('.')}
        
        if not app_index_info:
            # 如果没有应用索引，返回空列表
            return []
        
        # 按前缀分类索引
        prefix_groups = {}
        size_categories = {'large': [], 'medium': [], 'small': []}
        
        for index_name, info in app_index_info.items():
            # 确定前缀（应用索引）
            prefix = index_name.split('-')[0] if '-' in index_name else index_name.split('_')[0]
            
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append((index_name, info))
            
            # 按大小分类
            size_bytes = info['store_bytes']
            if size_bytes > 1024 * 1024 * 1024:  # > 1GB
                size_categories['large'].append((index_name, info))
            elif size_bytes > 100 * 1024 * 1024:  # > 100MB
                size_categories['medium'].append((index_name, info))
            else:
                size_categories['small'].append((index_name, info))
        
        # 1. 选择最大的几个索引 (8个)
        large_indices = sorted(size_categories['large'], key=lambda x: x[1]['store_bytes'], reverse=True)[:8]
        for index_name, info in large_indices:
            size_gb = info['store_bytes'] / (1024**3)
            typical_indices.append((index_name, info, f"大索引({size_gb:.1f}GB)"))
        
        # 2. 选择主要前缀的代表索引 (8个)
        main_prefixes = sorted(prefix_groups.items(), key=lambda x: len(x[1]), reverse=True)[:8]
        for prefix, indices in main_prefixes:
            if len([t for t in typical_indices if t[0] in [idx[0] for idx in indices]]) > 0:
                continue  # 已经包含了这个前缀的索引
            
            # 选择该前缀下最大的索引
            largest_in_prefix = max(indices, key=lambda x: x[1]['store_bytes'])
            index_name, info = largest_in_prefix
            
            # 确定类型描述
            if prefix == 'i':
                type_desc = "应用主索引"
            elif prefix == 'logs':
                type_desc = "日志索引"
            elif prefix == 'metrics':
                type_desc = "指标索引"
            elif prefix == 'geonames':
                type_desc = "地理数据索引"
            else:
                type_desc = f"{prefix}类索引"
            
            typical_indices.append((index_name, info, type_desc))
        
        # 3. 选择一些中等大小的索引 (2个)
        medium_indices = sorted(size_categories['medium'], key=lambda x: x[1]['store_bytes'], reverse=True)
        added_medium = 0
        for index_name, info in medium_indices:
            if added_medium >= 2:
                break
            if index_name not in [t[0] for t in typical_indices]:
                size_mb = info['store_bytes'] / (1024**2)
                typical_indices.append((index_name, info, f"中等索引({size_mb:.1f}MB)"))
                added_medium += 1
        
        # 4. 选择一些小索引 (2个)
        small_indices = sorted(size_categories['small'], key=lambda x: x[1]['docs'], reverse=True)
        added_small = 0
        for index_name, info in small_indices:
            if added_small >= 2:
                break
            if index_name not in [t[0] for t in typical_indices]:
                if info['docs'] > 0:
                    typical_indices.append((index_name, info, f"小索引({info['docs']:,}文档)"))
                else:
                    typical_indices.append((index_name, info, "空索引"))
                added_small += 1
        
        # 确保返回20个索引
        return typical_indices[:20]
    
    def _generate_index_health_analysis(self) -> str:
        """生成索引健康状态分析"""
        content = """### 5.3 索引健康状态分析

#### 5.3.1 索引状态分布

"""
        
        cluster_health = self.data_loader.get_cluster_health()
        indices_data = self.data_loader.load_json_file('indices.json')
        
        if not indices_data:
            content += "❌ **无法获取索引状态信息**\n\n"
            return content
        
        # 统计不同状态的索引
        index_status = {}
        problem_indices = []
        
        for shard in indices_data:
            index_name = shard.get('index', 'unknown')
            shard_state = shard.get('state', 'UNKNOWN')
            
            if index_name not in index_status:
                index_status[index_name] = {'states': set(), 'shard_count': 0}
            
            index_status[index_name]['states'].add(shard_state)
            index_status[index_name]['shard_count'] += 1
            
            # 检查问题分片
            if shard_state not in ['STARTED']:
                problem_indices.append({
                    'index': index_name,
                    'shard': shard.get('shard', 'N/A'),
                    'type': shard.get('prirep', 'N/A'),
                    'state': shard_state,
                    'node': shard.get('node', 'N/A')
                })
        
        # 计算健康状态统计
        green_indices = 0
        yellow_indices = 0
        red_indices = 0
        
        for index_name, info in index_status.items():
            states = info['states']
            if all(state == 'STARTED' for state in states):
                green_indices += 1
            elif any(state in ['UNASSIGNED', 'INITIALIZING'] for state in states):
                yellow_indices += 1
            else:
                red_indices += 1
        
        total_indices = len(index_status)
        
        content += f"""| 健康状态 | 索引数量 | 百分比 | 说明 |
|----------|----------|--------|------|
| 🟢 **绿色** | {green_indices} | {(green_indices/total_indices*100):.1f}% | 所有分片正常 |
| 🟡 **黄色** | {yellow_indices} | {(yellow_indices/total_indices*100):.1f}% | 部分副本分片异常 |
| 🔴 **红色** | {red_indices} | {(red_indices/total_indices*100):.1f}% | 主分片异常 |

"""
        
        # 问题索引详情
        if problem_indices:
            content += "#### 5.3.2 问题分片详情\n\n"
            content += "| 索引名称 | 分片ID | 类型 | 状态 | 节点 |\n"
            content += "|----------|--------|------|------|------|\n"
            
            # 显示前10个问题分片
            for problem in problem_indices[:10]:
                shard_type = "主分片" if problem['type'] == 'p' else "副本"
                content += f"| {problem['index']} | {problem['shard']} | {shard_type} | {problem['state']} | {problem['node']} |\n"
            
            if len(problem_indices) > 10:
                content += f"| ... | ... | ... | ... | ... |\n"
                content += f"| **共{len(problem_indices)}个问题分片** | | | | |\n"
        else:
            content += "#### 5.3.2 分片状态\n\n"
            content += "✅ **所有分片状态正常**\n"
        
        content += "\n"
        return content
    
    def _generate_index_patterns_distribution(self) -> str:
        """生成索引模式与分布"""
        content = """### 5.4 索引模式与分布

#### 5.4.1 索引命名模式分析

"""
        
        indices_data = self.data_loader.load_json_file('indices.json')
        if not indices_data:
            content += "❌ **无法获取索引信息**\n\n"
            return content
        
        # 提取所有唯一索引名
        index_names = set()
        for shard in indices_data:
            index_names.add(shard.get('index', 'unknown'))
        
        # 分析命名模式
        patterns = {
            'system_indices': [],  # 以.开头的系统索引
            'monitoring_indices': [],  # 监控相关
            'application_indices': [],  # 应用索引
            'time_series_indices': [],  # 时间序列索引
        }
        
        for index_name in sorted(index_names):
            if index_name.startswith('.'):
                patterns['system_indices'].append(index_name)
                if 'monitoring' in index_name:
                    patterns['monitoring_indices'].append(index_name)
            elif re.search(r'\d{4}[-\.]\d{2}[-\.]\d{2}', index_name):
                patterns['time_series_indices'].append(index_name)
            else:
                patterns['application_indices'].append(index_name)
        
        content += f"""| 索引类型 | 数量 | 示例 |
|----------|------|------|
| **系统索引** | {len(patterns['system_indices'])} | {', '.join(patterns['system_indices'][:3])}{'...' if len(patterns['system_indices']) > 3 else ''} |
| **监控索引** | {len(patterns['monitoring_indices'])} | {', '.join(patterns['monitoring_indices'][:3])}{'...' if len(patterns['monitoring_indices']) > 3 else ''} |
| **应用索引** | {len(patterns['application_indices'])} | {', '.join(patterns['application_indices'][:3])}{'...' if len(patterns['application_indices']) > 3 else ''} |
| **时间序列索引** | {len(patterns['time_series_indices'])} | {', '.join(patterns['time_series_indices'][:3])}{'...' if len(patterns['time_series_indices']) > 3 else ''} |

"""
        
        return content
    
    def _generate_shard_distribution_analysis(self) -> str:
        """生成分片分布分析"""
        content = """### 5.5 分片分布分析

#### 5.5.1 各节点分片分布

"""
        
        indices_data = self.data_loader.load_json_file('indices.json')
        if not indices_data:
            content += "❌ **无法获取分片信息**\n\n"
            return content
        
        # 统计各节点分片分布
        node_shard_stats = {}
        for shard in indices_data:
            node = shard.get('node', 'unknown')
            if node not in node_shard_stats:
                node_shard_stats[node] = {'primary': 0, 'replica': 0, 'total_size': 0}
            
            if shard.get('prirep') == 'p':
                node_shard_stats[node]['primary'] += 1
            else:
                node_shard_stats[node]['replica'] += 1
            
            # 累计存储大小
            store = shard.get('store')
            if store and store.isdigit():
                node_shard_stats[node]['total_size'] += int(store)
        
        # 按节点名排序
        sorted_nodes = sorted(node_shard_stats.items())
        
        content += "| 节点名称 | 主分片数 | 副本分片数 | 总分片数 | 分片数据大小 |\n"
        content += "|----------|----------|------------|----------|-------------|\n"
        
        for node, stats in sorted_nodes:
            total_shards = stats['primary'] + stats['replica']
            size_formatted = self.data_loader.format_bytes(stats['total_size'])
            content += f"| {node} | {stats['primary']} | {stats['replica']} | {total_shards} | {size_formatted} |\n"
        
        # 分片大小分布统计
        content += "\n#### 5.5.2 分片大小分布\n\n"
        
        shard_sizes = []
        for shard in indices_data:
            store = shard.get('store')
            if store and store.isdigit():
                shard_sizes.append(int(store))
        
        if shard_sizes:
            shard_sizes.sort()
            total_shards = len(shard_sizes)
            
            size_ranges = [
                ('< 1MB', lambda x: x < 1024*1024),
                ('1MB - 100MB', lambda x: 1024*1024 <= x < 100*1024*1024),
                ('100MB - 1GB', lambda x: 100*1024*1024 <= x < 1024*1024*1024),
                ('1GB - 10GB', lambda x: 1024*1024*1024 <= x < 10*1024*1024*1024),
                ('> 10GB', lambda x: x >= 10*1024*1024*1024)
            ]
            
            content += "| 分片大小范围 | 分片数量 | 百分比 |\n"
            content += "|--------------|----------|--------|\n"
            
            for range_name, range_func in size_ranges:
                count = sum(1 for size in shard_sizes if range_func(size))
                percentage = (count / total_shards) * 100
                content += f"| {range_name} | {count} | {percentage:.1f}% |\n"
            
            # 统计信息
            min_size = min(shard_sizes)
            max_size = max(shard_sizes)
            avg_size = sum(shard_sizes) // len(shard_sizes)
            median_size = shard_sizes[len(shard_sizes)//2]
            
            content += f"\n**分片大小统计**:\n"
            content += f"- 最小分片: {self.data_loader.format_bytes(min_size)}\n"
            content += f"- 最大分片: {self.data_loader.format_bytes(max_size)}\n"
            content += f"- 平均大小: {self.data_loader.format_bytes(avg_size)}\n"
            content += f"- 中位数: {self.data_loader.format_bytes(median_size)}\n"
        
        content += "\n"
        return content
    
    def _generate_index_performance_metrics(self) -> str:
        """生成索引性能指标"""
        content = """### 5.6 索引性能指标

#### 5.6.1 索引操作统计

"""
        
        nodes_stats = self.data_loader.get_nodes_stats()
        if not nodes_stats or 'nodes' not in nodes_stats:
            content += "❌ **无法获取性能指标**\n\n"
            return content
        
        # 汇总所有节点的索引操作统计
        total_indexing = 0
        total_delete = 0
        total_search = 0
        total_query_time = 0
        total_fetch_time = 0
        
        for node_id, stats in nodes_stats['nodes'].items():
            if 'indices' in stats:
                indices_stats = stats['indices']
                
                if 'indexing' in indices_stats:
                    total_indexing += indices_stats['indexing'].get('index_total', 0)
                    total_delete += indices_stats['indexing'].get('delete_total', 0)
                
                if 'search' in indices_stats:
                    total_search += indices_stats['search'].get('query_total', 0)
                    total_query_time += indices_stats['search'].get('query_time_in_millis', 0)
                    total_fetch_time += indices_stats['search'].get('fetch_time_in_millis', 0)
        
        avg_query_time = (total_query_time / total_search) if total_search > 0 else 0
        avg_fetch_time = (total_fetch_time / total_search) if total_search > 0 else 0
        
        content += f"""| 性能指标 | 数值 | 说明 |
|----------|------|------|
| **总索引操作数** | {total_indexing:,} | 集群累计索引文档次数 |
| **总删除操作数** | {total_delete:,} | 集群累计删除文档次数 |
| **总查询次数** | {total_search:,} | 集群累计查询次数 |
| **平均查询时间** | {avg_query_time:.2f}ms | 单次查询平均耗时 |
| **平均提取时间** | {avg_fetch_time:.2f}ms | 单次提取平均耗时 |

"""
        
        # 查询缓存统计
        cluster_stats = self.data_loader.get_cluster_stats()
        if cluster_stats and 'indices' in cluster_stats and 'query_cache' in cluster_stats['indices']:
            qc = cluster_stats['indices']['query_cache']
            cache_hit_rate = (qc.get('hit_count', 0) / qc.get('total_count', 1)) * 100
            
            content += "#### 5.6.2 查询缓存性能\n\n"
            content += f"""| 缓存指标 | 数值 | 说明 |
|----------|------|------|
| **缓存内存使用** | {qc.get('memory_size', 'N/A')} | 查询缓存占用内存 |
| **缓存命中率** | {cache_hit_rate:.1f}% | 查询缓存命中百分比 |
| **缓存总请求** | {qc.get('total_count', 0):,} | 查询缓存总请求数 |
| **缓存命中数** | {qc.get('hit_count', 0):,} | 查询缓存命中次数 |
| **缓存驱逐数** | {qc.get('evictions', 0):,} | 缓存条目被驱逐次数 |

"""
        
        content += "\n"
        return content
    
    def _generate_index_optimization_recommendations(self) -> str:
        """生成索引优化建议"""
        content = """### 5.7 索引优化建议

"""
        
        cluster_stats = self.data_loader.get_cluster_stats()
        indices_data = self.data_loader.load_json_file('indices.json')
        nodes_stats = self.data_loader.get_nodes_stats()
        
        issues = []
        recommendations = []
        
        # 获取数据节点数量
        data_node_count = 0
        if nodes_stats and 'nodes' in nodes_stats:
            for node_id, stats in nodes_stats['nodes'].items():
                if 'roles' in stats and 'data' in stats['roles']:
                    data_node_count += 1
        
        if indices_data:
            # 分析索引配置问题
            oversized_indices = []
            undersized_shards = []
            oversized_shards = []
            high_doc_count_indices = []
            inefficient_shard_distribution = []
            
            # 过滤应用索引
            app_indices = {}
            for shard in indices_data:
                index_name = shard.get('index', 'unknown')
                if index_name.startswith('.'):
                    continue  # 跳过系统索引
                
                if index_name not in app_indices:
                    app_indices[index_name] = {
                        'primary_shards': 0,
                        'docs': 0,
                        'total_size': 0,
                        'max_shard_size': 0
                    }
                
                if shard.get('prirep') == 'p':  # 只统计主分片
                    app_indices[index_name]['primary_shards'] += 1
                    
                    docs = shard.get('docs')
                    store = shard.get('store')
                    
                    if docs and docs.isdigit():
                        app_indices[index_name]['docs'] += int(docs)
                    
                    if store and store.isdigit():
                        shard_size = int(store)
                        app_indices[index_name]['total_size'] += shard_size
                        app_indices[index_name]['max_shard_size'] = max(
                            app_indices[index_name]['max_shard_size'], 
                            shard_size
                        )
            
            # 检查各类问题
            for index_name, info in app_indices.items():
                # 检查文档数量（200 million限制）
                if info['docs'] > 200_000_000:
                    high_doc_count_indices.append((index_name, info['docs']))
                
                # 检查分片大小（10GB-50GB合理范围）
                if info['max_shard_size'] > 50 * 1024**3:  # > 50GB
                    oversized_shards.append((index_name, info['max_shard_size']))
                elif info['max_shard_size'] < 10 * 1024**3 and info['docs'] > 1000:  # < 10GB 且有数据
                    undersized_shards.append((index_name, info['max_shard_size']))
                
                # 检查分片数量是否合理（相对于节点数量）
                if info['primary_shards'] > data_node_count * 2:  # 主分片数超过节点数的2倍
                    inefficient_shard_distribution.append((index_name, info['primary_shards']))
            
            # 生成问题报告
            if high_doc_count_indices:
                issues.append(f"发现{len(high_doc_count_indices)}个索引文档数超过2亿")
                for index_name, docs in high_doc_count_indices[:3]:
                    recommendations.append(f"索引 {index_name} 文档数({docs:,})过多，建议按时间或业务维度拆分")
            
            if oversized_shards:
                issues.append(f"发现{len(oversized_shards)}个索引分片超过50GB")
                for index_name, size in oversized_shards[:3]:
                    size_gb = size / (1024**3)
                    recommendations.append(f"索引 {index_name} 最大分片({size_gb:.1f}GB)过大，建议增加主分片数")
            
            if undersized_shards:
                issues.append(f"发现{len(undersized_shards)}个索引分片小于10GB")
                recommendations.append("小分片过多会影响性能，建议合并相关索引或减少主分片数")
            
            if inefficient_shard_distribution:
                issues.append(f"发现{len(inefficient_shard_distribution)}个索引分片分布不合理")
                recommendations.append(f"当前数据节点数({data_node_count})，建议主分片数不超过节点数的2倍")
        
        # 输出建议
        if issues:
            content += "#### 5.7.1 发现的配置问题\n\n"
            for issue in issues:
                content += f"- 🟡 {issue}\n"
            content += "\n"
        else:
            content += "#### 5.7.1 索引配置状态\n\n"
            content += "✅ **索引配置符合最佳实践**\n\n"
        
        content += "#### 5.7.2 优化建议\n\n"
        
        if recommendations:
            for rec in recommendations:
                content += f"- **{rec}**\n"
        else:
            content += "- 当前索引配置良好，建议继续保持\n"
        
        # 添加通用最佳实践
        content += "\n#### 5.7.3 索引配置最佳实践\n\n"
        content += f"""**分片配置原则**:
- 单个分片大小控制在10GB-50GB之间
- 单个索引文档数不超过2亿条
- 主分片数量不超过数据节点数的2倍（当前数据节点：{data_node_count}个）
- 优先通过控制分片大小而非过度分片来管理数据

**性能优化建议**:
- 定期监控分片分布均衡性
- 对历史数据考虑使用ILM进行生命周期管理
- 合理设置副本数，平衡可用性和存储成本
- 定期清理不使用的索引释放存储空间

"""
        
        return content
    
    def get_case_data(self) -> Dict[str, Any]:
        """获取用于检查的原始数据"""
        return {
            "cluster_stats": self.data_loader.get_cluster_stats(),
            "cluster_health": self.data_loader.get_cluster_health(),
            "indices_data": self.data_loader.load_json_file('indices.json')
        } 