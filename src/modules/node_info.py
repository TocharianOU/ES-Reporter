from typing import Dict, Any, List, Tuple
from datetime import datetime
from ..data_loader import ESDataLoader


class NodeInfoGenerator:
    """节点信息生成器"""
    
    def __init__(self, data_loader: ESDataLoader):
        self.data_loader = data_loader
    
    def generate(self) -> str:
        """生成节点信息内容"""
        nodes_info = self.data_loader.get_nodes()
        nodes_stats = self.data_loader.get_nodes_stats()
        nodes_usage = self.data_loader.load_json_file('nodes_usage.json')
        
        content = ""
        
        # 4.1 节点概览总表
        content += self._generate_nodes_overview(nodes_info, nodes_stats)
        
        # 4.2 硬件资源信息
        content += self._generate_hardware_resources(nodes_stats)
        
        # 4.3 JVM运行环境
        content += self._generate_jvm_environment(nodes_info, nodes_stats)
        
        # 4.4 节点角色与配置
        content += self._generate_node_roles_config(nodes_info)
        
        # 4.5 节点性能指标
        content += self._generate_performance_metrics(nodes_stats, nodes_usage)
        
        # 4.6 存储与分片分布
        content += self._generate_storage_shard_distribution(nodes_stats)
        
        # 4.7 异常与告警
        content += self._generate_alerts_recommendations(nodes_stats)
        
        return content
    
    def _generate_nodes_overview(self, nodes_info: Dict, nodes_stats: Dict) -> str:
        """生成节点概览总表"""
        content = """### 4.1 节点概览总表

| 节点名称 | IP地址 | 角色 | ES版本 | 运行时长 | CPU使用率 | 内存使用率 | 磁盘使用率 | 状态 |
|---------|--------|------|--------|----------|-----------|------------|------------|------|
"""
        
        if not nodes_info or 'nodes' not in nodes_info:
            content += "| N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | ⚠️ 无数据 |\n\n"
            return content
        
        # 按节点名称排序
        sorted_nodes = sorted(nodes_info['nodes'].items(), 
                            key=lambda x: x[1].get('name', ''))
        
        # 合并节点信息和统计信息
        for node_id, node_data in sorted_nodes:
            node_name = node_data.get('name', 'N/A')
            node_ip = node_data.get('ip', 'N/A')
            node_roles = ", ".join(node_data.get('roles', []))
            node_version = node_data.get('version', 'N/A')
            
            # 从节点统计中获取运行时长和资源使用
            uptime = "N/A"
            cpu_usage = "N/A"
            mem_usage = "N/A"
            disk_usage = "N/A"
            status = "🟢"
            
            if nodes_stats and 'nodes' in nodes_stats and node_id in nodes_stats['nodes']:
                stats = nodes_stats['nodes'][node_id]
                
                # 计算运行时长
                if 'jvm' in stats and 'start_time_in_millis' in stats['jvm']:
                    start_time = stats['jvm']['start_time_in_millis']
                    current_time = stats.get('timestamp', 0)
                    if current_time and start_time:
                        uptime_ms = current_time - start_time
                        uptime_days = uptime_ms // (24 * 60 * 60 * 1000)
                        uptime = f"{uptime_days}天"
                
                # CPU使用率
                if 'os' in stats and 'cpu' in stats['os']:
                    cpu_percent = stats['os']['cpu'].get('percent', 0)
                    cpu_usage = f"{cpu_percent}%"
                
                # 内存使用率
                if 'jvm' in stats and 'mem' in stats['jvm']:
                    jvm_mem = stats['jvm']['mem']
                    heap_used = jvm_mem.get('heap_used_in_bytes', 0)
                    heap_max = jvm_mem.get('heap_max_in_bytes', 1)
                    if heap_max > 0:
                        mem_percent = (heap_used / heap_max) * 100
                        mem_usage = f"{mem_percent:.1f}%"
                
                # 磁盘使用率（简化计算）
                if 'fs' in stats and 'total' in stats['fs']:
                    fs_total = stats['fs']['total']
                    total_bytes = fs_total.get('total_in_bytes', 1)
                    free_bytes = fs_total.get('free_in_bytes', 0)
                    if total_bytes > 0:
                        used_bytes = total_bytes - free_bytes
                        disk_percent = (used_bytes / total_bytes) * 100
                        disk_usage = f"{disk_percent:.1f}%"
            
            content += f"| {node_name} | {node_ip} | {node_roles} | {node_version} | {uptime} | {cpu_usage} | {mem_usage} | {disk_usage} | {status} |\n"
        
        content += "\n"
        return content
    
    def _generate_hardware_resources(self, nodes_stats: Dict) -> str:
        """生成硬件资源信息"""
        content = """### 4.2 硬件资源信息

#### 4.2.1 CPU资源概览

| 节点名称 | CPU核心数 | 可用核心数 | CPU使用率 | 负载(1m/5m/15m) |
|---------|-----------|------------|-----------|-----------------|
"""
        
        if not nodes_stats or 'nodes' not in nodes_stats:
            content += "| N/A | N/A | N/A | N/A | N/A |\n\n"
        else:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_stats['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, stats in sorted_nodes:
                node_name = stats.get('name', 'N/A')
                
                # CPU信息
                cpu_cores = "N/A"
                available_cores = "N/A"
                cpu_percent = "N/A"
                load_avg = "N/A"
                
                if 'os' in stats:
                    if 'available_processors' in stats['os']:
                        available_cores = stats['os']['available_processors']
                    if 'allocated_processors' in stats['os']:
                        cpu_cores = stats['os']['allocated_processors']
                    if 'cpu' in stats['os']:
                        cpu_percent = f"{stats['os']['cpu'].get('percent', 0)}%"
                        load_info = stats['os']['cpu'].get('load_average', {})
                        if load_info:
                            load_1m = load_info.get('1m', 0)
                            load_5m = load_info.get('5m', 0)
                            load_15m = load_info.get('15m', 0)
                            load_avg = f"{load_1m:.2f}/{load_5m:.2f}/{load_15m:.2f}"
                
                content += f"| {node_name} | {cpu_cores} | {available_cores} | {cpu_percent} | {load_avg} |\n"
        
        content += """
#### 4.2.2 内存资源概览

| 节点名称 | 系统内存 | JVM堆内存(最大) | JVM堆内存(已用) | 堆使用率 |
|---------|----------|-----------------|-----------------|----------|
"""
        
        if nodes_stats and 'nodes' in nodes_stats:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_stats['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, stats in sorted_nodes:
                node_name = stats.get('name', 'N/A')
                
                # 内存信息
                system_mem = "N/A"
                heap_max = "N/A"
                heap_used = "N/A"
                heap_percent = "N/A"
                
                if 'os' in stats and 'mem' in stats['os']:
                    system_mem = stats['os']['mem'].get('total', 'N/A')
                
                if 'jvm' in stats and 'mem' in stats['jvm']:
                    jvm_mem = stats['jvm']['mem']
                    heap_max = jvm_mem.get('heap_max', 'N/A')
                    heap_used = jvm_mem.get('heap_used', 'N/A')
                    
                    heap_used_bytes = jvm_mem.get('heap_used_in_bytes', 0)
                    heap_max_bytes = jvm_mem.get('heap_max_in_bytes', 1)
                    if heap_max_bytes > 0:
                        heap_percent = f"{(heap_used_bytes / heap_max_bytes) * 100:.1f}%"
                
                content += f"| {node_name} | {system_mem} | {heap_max} | {heap_used} | {heap_percent} |\n"
        
        content += "\n"
        return content
    
    def _generate_jvm_environment(self, nodes_info: Dict, nodes_stats: Dict) -> str:
        """生成JVM运行环境信息"""
        content = """### 4.3 JVM运行环境

#### 4.3.1 JVM版本与配置

| 节点名称 | Java版本 | JVM版本 | GC收集器 | 堆大小配置 |
|---------|----------|---------|----------|------------|
"""
        
        if not nodes_info or 'nodes' not in nodes_info:
            content += "| N/A | N/A | N/A | N/A | N/A |\n\n"
        else:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_info['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, node_data in sorted_nodes:
                node_name = node_data.get('name', 'N/A')
                
                # JVM信息
                java_version = "N/A"
                jvm_version = "N/A"
                gc_collectors = "N/A"
                heap_config = "N/A"
                
                if 'jvm' in node_data:
                    jvm_info = node_data['jvm']
                    java_version = jvm_info.get('version', 'N/A')
                    jvm_version = f"{jvm_info.get('vm_name', 'N/A')} {jvm_info.get('vm_version', '')}"
                    
                    gc_list = jvm_info.get('gc_collectors', [])
                    if gc_list:
                        gc_collectors = ", ".join(gc_list)
                    
                    if 'mem' in jvm_info:
                        heap_init = jvm_info['mem'].get('heap_init', 'N/A')
                        heap_max = jvm_info['mem'].get('heap_max', 'N/A')
                        heap_config = f"初始:{heap_init} 最大:{heap_max}"
                
                content += f"| {node_name} | {java_version} | {jvm_version} | {gc_collectors} | {heap_config} |\n"
        
        content += """
#### 4.3.2 GC性能统计

| 节点名称 | Young GC(次数/时间) | Old GC(次数/时间) | GC总耗时占比 |
|---------|-------------------|------------------|--------------|
"""
        
        if nodes_stats and 'nodes' in nodes_stats:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_stats['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, stats in sorted_nodes:
                node_name = stats.get('name', 'N/A')
                
                young_gc = "N/A"
                old_gc = "N/A"
                gc_overhead = "N/A"
                
                if 'jvm' in stats and 'gc' in stats['jvm']:
                    gc_info = stats['jvm']['gc']
                    collectors = gc_info.get('collectors', {})
                    
                    # 分析不同的GC收集器
                    for gc_name, gc_data in collectors.items():
                        if 'young' in gc_name.lower() or 'eden' in gc_name.lower():
                            count = gc_data.get('collection_count', 0)
                            time_ms = gc_data.get('collection_time_in_millis', 0)
                            young_gc = f"{count}次/{time_ms}ms"
                        elif 'old' in gc_name.lower():
                            count = gc_data.get('collection_count', 0)
                            time_ms = gc_data.get('collection_time_in_millis', 0)
                            old_gc = f"{count}次/{time_ms}ms"
                
                content += f"| {node_name} | {young_gc} | {old_gc} | {gc_overhead} |\n"
        
        content += "\n"
        return content
    
    def _generate_node_roles_config(self, nodes_info: Dict) -> str:
        """生成节点角色与配置信息"""
        content = """### 4.4 节点角色与配置

#### 4.4.1 节点角色分配详情

| 节点名称 | 主要角色 | 所有角色 | 节点属性 |
|---------|----------|----------|----------|
"""
        
        if not nodes_info or 'nodes' not in nodes_info:
            content += "| N/A | N/A | N/A | N/A |\n\n"
        else:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_info['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, node_data in sorted_nodes:
                node_name = node_data.get('name', 'N/A')
                roles = node_data.get('roles', [])
                
                # 确定主要角色
                primary_role = "coordinating"
                if 'master' in roles:
                    primary_role = "master"
                elif 'data' in roles:
                    primary_role = "data"
                elif 'ingest' in roles:
                    primary_role = "ingest"
                
                all_roles = ", ".join(roles) if roles else "N/A"
                
                # 节点属性
                attributes = node_data.get('attributes', {})
                attr_list = []
                for key, value in attributes.items():
                    attr_list.append(f"{key}:{value}")
                node_attrs = ", ".join(attr_list) if attr_list else "无"
                
                content += f"| {node_name} | {primary_role} | {all_roles} | {node_attrs} |\n"
        
        content += "\n"
        return content
    
    def _generate_performance_metrics(self, nodes_stats: Dict, nodes_usage: Dict) -> str:
        """生成节点性能指标"""
        content = """### 4.5 节点性能指标

#### 4.5.1 索引操作统计

| 节点名称 | 索引操作数 | 删除操作数 | 查询操作数 | 平均查询时间 |
|---------|------------|------------|------------|--------------|
"""
        
        if not nodes_stats or 'nodes' not in nodes_stats:
            content += "| N/A | N/A | N/A | N/A | N/A |\n\n"
        else:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_stats['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, stats in sorted_nodes:
                node_name = stats.get('name', 'N/A')
                
                index_total = "N/A"
                delete_total = "N/A"
                search_total = "N/A"
                avg_search_time = "N/A"
                
                if 'indices' in stats:
                    indices_stats = stats['indices']
                    
                    # 索引操作
                    if 'indexing' in indices_stats:
                        index_total = indices_stats['indexing'].get('index_total', 'N/A')
                        delete_total = indices_stats['indexing'].get('delete_total', 'N/A')
                    
                    # 搜索操作
                    if 'search' in indices_stats:
                        search_stats = indices_stats['search']
                        search_total = search_stats.get('query_total', 'N/A')
                        query_time = search_stats.get('query_time_in_millis', 0)
                        query_count = search_stats.get('query_total', 1)
                        if query_count > 0:
                            avg_search_time = f"{query_time / query_count:.2f}ms"
                
                content += f"| {node_name} | {index_total} | {delete_total} | {search_total} | {avg_search_time} |\n"
        
        content += "\n"
        return content
    
    def _generate_storage_shard_distribution(self, nodes_stats: Dict) -> str:
        """生成存储与分片分布信息"""
        content = """### 4.6 存储与分片分布

#### 4.6.1 节点存储使用情况

| 节点名称 | 总存储空间 | 已用空间 | 可用空间 | 使用率 | 分片数量 |
|---------|------------|----------|----------|--------|----------|
"""
        
        if not nodes_stats or 'nodes' not in nodes_stats:
            content += "| N/A | N/A | N/A | N/A | N/A | N/A |\n\n"
        else:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_stats['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, stats in sorted_nodes:
                node_name = stats.get('name', 'N/A')
                
                total_space = "N/A"
                used_space = "N/A"
                free_space = "N/A"
                usage_percent = "N/A"
                shard_count = "N/A"
                
                # 文件系统信息
                if 'fs' in stats and 'total' in stats['fs']:
                    fs_total = stats['fs']['total']
                    total_bytes = fs_total.get('total_in_bytes', 0)
                    free_bytes = fs_total.get('free_in_bytes', 0)
                    
                    if total_bytes > 0:
                        used_bytes = total_bytes - free_bytes
                        total_space = self.data_loader.format_bytes(total_bytes)
                        used_space = self.data_loader.format_bytes(used_bytes)
                        free_space = self.data_loader.format_bytes(free_bytes)
                        usage_percent = f"{(used_bytes / total_bytes) * 100:.1f}%"
                
                # 分片信息（从indices统计中获取）
                if 'indices' in stats and 'shards' in stats['indices']:
                    shard_count = len(stats['indices']['shards'])
                
                content += f"| {node_name} | {total_space} | {used_space} | {free_space} | {usage_percent} | {shard_count} |\n"
        
        content += "\n"
        return content
    
    def _generate_alerts_recommendations(self, nodes_stats: Dict) -> str:
        """生成异常与告警信息"""
        content = """### 4.7 异常与告警

#### 4.7.1 资源告警检查

"""
        
        alerts = []
        recommendations = []
        
        if nodes_stats and 'nodes' in nodes_stats:
            # 按节点名称排序
            sorted_nodes = sorted(nodes_stats['nodes'].items(), 
                                key=lambda x: x[1].get('name', ''))
            
            for node_id, stats in sorted_nodes:
                node_name = stats.get('name', 'N/A')
                
                # 检查CPU使用率
                if 'os' in stats and 'cpu' in stats['os']:
                    cpu_percent = stats['os']['cpu'].get('percent', 0)
                    if cpu_percent > 80:
                        alerts.append(f"🔴 **{node_name}**: CPU使用率过高 ({cpu_percent}%)")
                    elif cpu_percent > 60:
                        alerts.append(f"🟡 **{node_name}**: CPU使用率较高 ({cpu_percent}%)")
                
                # 检查内存使用率
                if 'jvm' in stats and 'mem' in stats['jvm']:
                    jvm_mem = stats['jvm']['mem']
                    heap_used = jvm_mem.get('heap_used_in_bytes', 0)
                    heap_max = jvm_mem.get('heap_max_in_bytes', 1)
                    if heap_max > 0:
                        heap_percent = (heap_used / heap_max) * 100
                        if heap_percent > 85:
                            alerts.append(f"🔴 **{node_name}**: JVM堆内存使用率过高 ({heap_percent:.1f}%)")
                        elif heap_percent > 70:
                            alerts.append(f"🟡 **{node_name}**: JVM堆内存使用率较高 ({heap_percent:.1f}%)")
                
                # 检查磁盘使用率
                if 'fs' in stats and 'total' in stats['fs']:
                    fs_total = stats['fs']['total']
                    total_bytes = fs_total.get('total_in_bytes', 1)
                    free_bytes = fs_total.get('free_in_bytes', 0)
                    if total_bytes > 0:
                        used_bytes = total_bytes - free_bytes
                        disk_percent = (used_bytes / total_bytes) * 100
                        if disk_percent > 90:
                            alerts.append(f"🔴 **{node_name}**: 磁盘使用率过高 ({disk_percent:.1f}%)")
                        elif disk_percent > 80:
                            alerts.append(f"🟡 **{node_name}**: 磁盘使用率较高 ({disk_percent:.1f}%)")
        
        if alerts:
            content += "**当前告警**:\n"
            for alert in alerts:
                content += f"- {alert}\n"
            content += "\n"
        else:
            content += "✅ **当前无资源告警**\n\n"
        
        # 通用建议
        content += """#### 4.7.2 优化建议

**资源优化建议**:
- 定期监控CPU、内存、磁盘使用率
- 当JVM堆内存使用率持续超过70%时，考虑增加堆内存或优化查询
- 磁盘使用率超过80%时，建议清理旧数据或扩容存储
- 监控GC频率，频繁的Full GC可能影响性能

**配置建议**:
- 确保所有节点的ES版本一致
- 检查节点间的网络连接质量
- 定期检查节点的负载分布是否均衡

"""
        
        return content
    
    def get_case_data(self) -> Dict[str, Any]:
        """获取用于检查的原始数据"""
        return {
            "nodes_info": self.data_loader.get_nodes(),
            "nodes_stats": self.data_loader.get_nodes_stats(),
            "nodes_usage": self.data_loader.load_json_file('nodes_usage.json')
        } 