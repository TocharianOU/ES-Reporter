import os
import gzip
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict, Counter
from ..data_loader import ESDataLoader


class LogAnalysisGenerator:
    """日志分析生成器"""
    
    def __init__(self, data_loader: ESDataLoader):
        self.data_loader = data_loader
        self.logs_dir = os.path.join(data_loader.data_dir, 'logs')
    
    def generate(self) -> str:
        """生成日志分析内容"""
        content = ""
        
        # 6.1 日志文件概览
        content += self._generate_log_overview()
        
        # 6.2 错误日志分析
        content += self._generate_error_analysis()
        
        # 6.3 警告信息分析
        content += self._generate_warning_analysis()
        
        # 6.4 日志累积情况分析
        content += self._generate_log_accumulation_analysis()
        
        # 6.5 重要事件分析
        content += self._generate_important_events_analysis()
        
        return content
    
    def _generate_log_overview(self) -> str:
        """生成日志文件概览"""
        content = """### 6.1 日志文件概览

"""
        
        if not os.path.exists(self.logs_dir):
            content += "❌ **日志目录不存在**，无法进行日志分析\n\n"
            return content
        
        log_files = []
        total_size = 0
        
        try:
            for filename in os.listdir(self.logs_dir):
                if filename.endswith('.log') or filename.endswith('.log.gz'):
                    file_path = os.path.join(self.logs_dir, filename)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        # 获取文件修改时间
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        log_files.append({
                            'name': filename,
                            'size': file_size,
                            'modified': mod_time,
                            'compressed': filename.endswith('.gz')
                        })
        except Exception as e:
            content += f"❌ **读取日志目录失败**: {e}\n\n"
            return content
        
        if not log_files:
            content += "⚠️ **未发现日志文件**\n\n"
            return content
        
        # 按修改时间排序
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        
        content += f"""#### 6.1.1 日志文件统计

| 文件统计 | 数值 | 说明 |
|----------|------|------|
| **日志文件总数** | {len(log_files)} | 包含压缩和未压缩文件 |
| **总占用空间** | {self._format_size(total_size)} | 所有日志文件大小 |
| **最新文件** | {log_files[0]['name']} | 最近修改的日志文件 |
| **最新更新时间** | {log_files[0]['modified'].strftime('%Y-%m-%d %H:%M:%S')} | 日志最后更新时间 |

"""
        
        # 文件详情
        content += "#### 6.1.2 日志文件详情\n\n"
        content += "| 文件名 | 大小 | 修改时间 | 类型 | 状态 |\n"
        content += "|--------|------|----------|------|------|\n"
        
        for log_file in log_files[:10]:  # 显示最新的10个文件
            file_type = "压缩日志" if log_file['compressed'] else "当前日志"
            status = "🟢" if not log_file['compressed'] else "📦"
            
            content += f"| {log_file['name']} | {self._format_size(log_file['size'])} | {log_file['modified'].strftime('%Y-%m-%d %H:%M:%S')} | {file_type} | {status} |\n"
        
        if len(log_files) > 10:
            content += f"| ... | ... | ... | ... | ... |\n"
            content += f"| **共{len(log_files)}个文件** | | | | |\n"
        
        content += "\n"
        return content
    
    def _generate_error_analysis(self) -> str:
        """生成错误日志分析"""
        content = """### 6.2 错误日志分析

"""
        
        errors = self._extract_log_entries(['ERROR', 'FATAL'])
        
        if not errors:
            content += "✅ **未发现ERROR或FATAL级别的错误日志**\n\n"
            return content
        
        # 按错误类型统计
        error_types = Counter()
        error_examples = defaultdict(list)
        
        for error in errors:
            error_type = self._extract_error_type(error['message'])
            error_types[error_type] += 1
            if len(error_examples[error_type]) < 3:  # 保存前3个例子
                error_examples[error_type].append(error)
        
        content += f"""#### 6.2.1 错误统计

| 错误类型 | 出现次数 | 最近发生时间 |
|----------|----------|--------------|
"""
        
        for error_type, count in error_types.most_common(10):
            latest_error = max(error_examples[error_type], key=lambda x: x['timestamp'])
            content += f"| {error_type} | {count} | {latest_error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} |\n"
        
        # 详细错误信息
        if error_types:
            content += "\n#### 6.2.2 重要错误详情\n\n"
            
            for error_type, count in list(error_types.most_common(3)):
                content += f"**{error_type}** (共{count}次):\n"
                for example in error_examples[error_type][:2]:
                    content += f"- {example['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: {example['message'][:200]}...\n"
                content += "\n"
        
        content += "\n"
        return content
    
    def _generate_warning_analysis(self) -> str:
        """生成警告信息分析"""
        content = """### 6.3 警告信息分析

"""
        
        warnings = self._extract_log_entries(['WARN'])
        
        if not warnings:
            content += "✅ **未发现WARN级别的警告日志**\n\n"
            return content
        
        # 按警告类型统计
        warning_types = Counter()
        warning_examples = defaultdict(list)
        
        for warning in warnings:
            warning_type = self._extract_warning_type(warning['message'])
            warning_types[warning_type] += 1
            if len(warning_examples[warning_type]) < 2:
                warning_examples[warning_type].append(warning)
        
        content += f"""#### 6.3.1 警告统计

| 警告类型 | 出现次数 | 严重程度 | 最近发生时间 |
|----------|----------|----------|--------------|
"""
        
        for warning_type, count in warning_types.most_common(10):
            severity = self._assess_warning_severity(warning_type, count)
            latest_warning = max(warning_examples[warning_type], key=lambda x: x['timestamp'])
            content += f"| {warning_type} | {count} | {severity} | {latest_warning['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} |\n"
        
        # 高频警告分析
        high_freq_warnings = [(wt, count) for wt, count in warning_types.items() if count > 10]
        if high_freq_warnings:
            content += "\n#### 6.3.2 高频警告分析\n\n"
            content += "以下警告出现频率较高，建议重点关注：\n\n"
            
            for warning_type, count in sorted(high_freq_warnings, key=lambda x: x[1], reverse=True)[:5]:
                content += f"**{warning_type}** (出现{count}次)\n"
                content += f"- 建议操作: {self._get_warning_suggestion(warning_type)}\n\n"
        
        content += "\n"
        return content
    
    def _generate_log_accumulation_analysis(self) -> str:
        """生成日志累积情况分析"""
        content = """### 6.4 日志累积情况分析

"""
        
        if not os.path.exists(self.logs_dir):
            content += "❌ **日志目录不存在**\n\n"
            return content
        
        # 分析日志文件数量和大小
        log_files = []
        total_size = 0
        current_log_size = 0
        compressed_count = 0
        
        try:
            for filename in os.listdir(self.logs_dir):
                if filename.endswith('.log') or filename.endswith('.log.gz'):
                    file_path = os.path.join(self.logs_dir, filename)
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
        except Exception as e:
            content += f"❌ **分析日志累积失败**: {e}\n\n"
            return content
        
        # 累积情况评估
        accumulation_status = "正常"
        recommendations = []
        
        if len(log_files) > 50:
            accumulation_status = "过多"
            recommendations.append("日志文件数量过多，建议定期清理历史日志")
        elif len(log_files) > 20:
            accumulation_status = "较多"
            recommendations.append("日志文件数量较多，建议配置日志轮转策略")
        
        if total_size > 1024 * 1024 * 1024:  # 超过1GB
            accumulation_status = "过多"
            recommendations.append("日志总大小超过1GB，建议清理或压缩")
        elif total_size > 500 * 1024 * 1024:  # 超过500MB
            if accumulation_status == "正常":
                accumulation_status = "适中"
            recommendations.append("日志大小适中，建议监控增长趋势")
        
        if current_log_size > 100 * 1024 * 1024:  # 当前日志超过100MB
            recommendations.append("当前日志文件较大，建议检查是否有异常日志输出")
        
        status_icon = {"正常": "✅", "适中": "🟡", "较多": "🟡", "过多": "🔴"}.get(accumulation_status, "⚪")
        
        content += f"""#### 6.4.1 累积情况统计

| 累积指标 | 数值 | 状态 |
|----------|------|------|
| **总文件数** | {len(log_files)} | {status_icon} |
| **压缩文件数** | {compressed_count} | ✅ |
| **当前日志大小** | {self._format_size(current_log_size)} | {"🟡" if current_log_size > 50*1024*1024 else "✅"} |
| **总占用空间** | {self._format_size(total_size)} | {status_icon} |
| **累积状况** | {accumulation_status} | {status_icon} |

"""
        
        if recommendations:
            content += "#### 6.4.2 优化建议\n\n"
            for i, rec in enumerate(recommendations, 1):
                priority = "🔴 高" if "过多" in rec else "🟡 中" if "较多" in rec else "🟢 低"
                content += f"{i}. **{priority}优先级**: {rec}\n"
            content += "\n"
        
        return content
    
    def _generate_important_events_analysis(self) -> str:
        """生成重要事件分析"""
        content = """### 6.5 重要事件分析

"""
        
        # 提取重要事件
        important_events = self._extract_important_events()
        
        if not important_events:
            content += "✅ **未发现需要特别关注的重要事件**\n\n"
            return content
        
        # 按事件类型分类
        event_categories = {
            'cluster_changes': [],
            'node_events': [],
            'shard_events': [],
            'performance_issues': [],
            'other': []
        }
        
        for event in important_events:
            category = self._categorize_event(event['message'])
            event_categories[category].append(event)
        
        content += "#### 6.5.1 重要事件概览\n\n"
        
        for category, events in event_categories.items():
            if events:
                category_name = {
                    'cluster_changes': '集群状态变更',
                    'node_events': '节点事件',
                    'shard_events': '分片事件',
                    'performance_issues': '性能问题',
                    'other': '其他事件'
                }.get(category, category)
                
                content += f"**{category_name}** ({len(events)}个事件):\n"
                
                # 显示最近的几个事件
                for event in sorted(events, key=lambda x: x['timestamp'], reverse=True)[:3]:
                    content += f"- {event['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: {event['message'][:150]}...\n"
                content += "\n"
        
        return content
    
    def _extract_log_entries(self, levels: List[str]) -> List[Dict]:
        """提取指定级别的日志条目"""
        entries = []
        
        if not os.path.exists(self.logs_dir):
            return entries
        
        try:
            for filename in os.listdir(self.logs_dir):
                if filename.endswith('.log'):  # 只分析未压缩的日志
                    file_path = os.path.join(self.logs_dir, filename)
                    entries.extend(self._parse_log_file(file_path, levels))
        except Exception as e:
            print(f"提取日志条目失败: {e}")
        
        return entries
    
    def _parse_log_file(self, file_path: str, levels: List[str]) -> List[Dict]:
        """解析单个日志文件"""
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析日志格式 [timestamp][LEVEL][component] message
                    match = re.match(r'\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\s*(.+)', line)
                    if match:
                        timestamp_str, level, component, message = match.groups()
                        
                        if level in levels:
                            try:
                                # 解析时间戳
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S,%f')
                                entries.append({
                                    'timestamp': timestamp,
                                    'level': level,
                                    'component': component,
                                    'message': message,
                                    'file': os.path.basename(file_path)
                                })
                            except ValueError:
                                # 时间戳解析失败，跳过这条日志
                                continue
        except Exception as e:
            print(f"解析日志文件 {file_path} 失败: {e}")
        
        return entries
    
    def _extract_important_events(self) -> List[Dict]:
        """提取重要事件"""
        # 定义重要事件的关键字
        important_keywords = [
            'ClusterApplierService', 'removed', 'added', 'master', 'node',
            'shard', 'allocation', 'recovery', 'timeout', 'exception'
        ]
        
        events = []
        
        if not os.path.exists(self.logs_dir):
            return events
        
        try:
            for filename in os.listdir(self.logs_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(self.logs_dir, filename)
                    events.extend(self._parse_important_events(file_path, important_keywords))
        except Exception as e:
            print(f"提取重要事件失败: {e}")
        
        return events
    
    def _parse_important_events(self, file_path: str, keywords: List[str]) -> List[Dict]:
        """解析重要事件"""
        events = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检查是否包含重要关键字
                    if any(keyword in line for keyword in keywords):
                        match = re.match(r'\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\s*(.+)', line)
                        if match:
                            timestamp_str, level, component, message = match.groups()
                            
                            try:
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S,%f')
                                events.append({
                                    'timestamp': timestamp,
                                    'level': level,
                                    'component': component,
                                    'message': message,
                                    'file': os.path.basename(file_path)
                                })
                            except ValueError:
                                continue
        except Exception as e:
            print(f"解析重要事件文件 {file_path} 失败: {e}")
        
        return events
    
    def _extract_error_type(self, message: str) -> str:
        """提取错误类型"""
        # 简化的错误类型提取
        if 'Exception' in message:
            return '系统异常'
        elif 'timeout' in message.lower():
            return '超时错误'
        elif 'connection' in message.lower():
            return '连接错误'
        elif 'allocation' in message.lower():
            return '分配错误'
        elif 'shard' in message.lower():
            return '分片错误'
        else:
            return '其他错误'
    
    def _extract_warning_type(self, message: str) -> str:
        """提取警告类型"""
        if 'heap' in message.lower():
            return '内存使用警告'
        elif 'disk' in message.lower():
            return '磁盘空间警告'
        elif 'slow' in message.lower():
            return '性能警告'
        elif 'connection' in message.lower():
            return '连接警告'
        elif 'timeout' in message.lower():
            return '超时警告'
        else:
            return '其他警告'
    
    def _assess_warning_severity(self, warning_type: str, count: int) -> str:
        """评估警告严重程度"""
        if count > 100:
            return "🔴 高"
        elif count > 20:
            return "🟡 中"
        else:
            return "🟢 低"
    
    def _get_warning_suggestion(self, warning_type: str) -> str:
        """获取警告建议"""
        suggestions = {
            '内存使用警告': '监控JVM堆内存使用，考虑调整堆大小或优化查询',
            '磁盘空间警告': '清理日志文件，扩展存储空间或配置数据清理策略',
            '性能警告': '检查系统负载和资源使用情况，优化索引结构',
            '连接警告': '检查网络连接稳定性，调整超时配置',
            '超时警告': '调整超时参数，检查系统负载和网络延迟'
        }
        return suggestions.get(warning_type, '根据具体情况进行分析和处理')
    
    def _categorize_event(self, message: str) -> str:
        """事件分类"""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['added', 'removed', 'master', 'cluster']):
            return 'cluster_changes'
        elif 'node' in message_lower:
            return 'node_events'
        elif 'shard' in message_lower:
            return 'shard_events'
        elif any(keyword in message_lower for keyword in ['slow', 'timeout', 'performance']):
            return 'performance_issues'
        else:
            return 'other'
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
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
        log_files = []
        errors = []
        warnings = []
        
        if os.path.exists(self.logs_dir):
            try:
                for filename in os.listdir(self.logs_dir):
                    if filename.endswith('.log') or filename.endswith('.log.gz'):
                        file_path = os.path.join(self.logs_dir, filename)
                        if os.path.isfile(file_path):
                            log_files.append({
                                'name': filename,
                                'size': os.path.getsize(file_path),
                                'compressed': filename.endswith('.gz')
                            })
                
                errors = self._extract_log_entries(['ERROR', 'FATAL'])
                warnings = self._extract_log_entries(['WARN'])
            except Exception as e:
                print(f"获取日志case数据失败: {e}")
        
        return {
            "log_files": log_files,
            "errors": [{'timestamp': e['timestamp'].isoformat(), 'level': e['level'], 'message': e['message']} for e in errors[:50]],
            "warnings": [{'timestamp': w['timestamp'].isoformat(), 'level': w['level'], 'message': w['message']} for w in warnings[:50]],
            "important_events": [{'timestamp': ie['timestamp'].isoformat(), 'level': ie['level'], 'message': ie['message']} for ie in self._extract_important_events()[:30]]
        } 