import os
import json
from datetime import datetime
from typing import Dict, Any
from .data_loader import ESDataLoader
from .modules import ReportOverviewGenerator, ExecutiveSummaryGenerator, ClusterBasicInfoGenerator, NodeInfoGenerator
from .modules.index_analysis import IndexAnalysisGenerator
from .modules.data_governance import FinalRecommendationsGenerator
from .modules.log_analysis import LogAnalysisGenerator
from .i18n import I18n


class ESReportGenerator:
    """Elasticsearch报告生成器"""
    
    def __init__(self, data_dir: str, output_dir: str = "output", language: str = "zh"):
        """
        初始化报告生成器
        
        Args:
            data_dir: 诊断数据目录路径
            output_dir: 输出目录路径
            language: 报告语言 ('zh' 或 'en')
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.language = language
        self.i18n = I18n(language)  # 初始化国际化
        self.data_loader = ESDataLoader(data_dir)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "cases"), exist_ok=True)
        
        # 初始化生成器，传递语言参数
        self.generators = {
            'REPORT_OVERVIEW': ReportOverviewGenerator(self.data_loader, language),
            'EXECUTIVE_SUMMARY': ExecutiveSummaryGenerator(self.data_loader, language),
            'CLUSTER_BASIC_INFO': ClusterBasicInfoGenerator(self.data_loader, language),
            'NODE_INFO': NodeInfoGenerator(self.data_loader, language),
            'INDEX_ANALYSIS': IndexAnalysisGenerator(self.data_loader, language),
            'FINAL_RECOMMENDATIONS': FinalRecommendationsGenerator(self.data_loader, language),
            'LOG_ANALYSIS': LogAnalysisGenerator(self.data_loader, language)
        }
    
    def load_template(self) -> str:
        """加载报告模板"""
        template_path = "templates/report_template.md"
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # 使用内置模板
            return self.get_default_template()
    
    def get_default_template(self) -> str:
        """获取默认模板"""
        if self.language == 'en':
            return """# Elasticsearch Cluster Inspection Report

## 1. Report Overview

{{REPORT_OVERVIEW}}

## 2. Executive Summary

{{EXECUTIVE_SUMMARY}}

## 3. Cluster Basic Information

{{CLUSTER_BASIC_INFO}}

## 4. Node Information

{{NODE_INFO}}

## 5. Index Analysis

{{INDEX_ANALYSIS}}

## 6. Log Analysis

{{LOG_ANALYSIS}}

## 7. Final Recommendations

{{FINAL_RECOMMENDATIONS}}"""
        else:
            return """# Elasticsearch 集群巡检报告

## 1. 报告概述

{{REPORT_OVERVIEW}}

## 2. 执行摘要

{{EXECUTIVE_SUMMARY}}

## 3. 集群基础信息

{{CLUSTER_BASIC_INFO}}

## 4. 节点信息

{{NODE_INFO}}

## 5. 索引分析

{{INDEX_ANALYSIS}}

## 6. 日志分析

{{LOG_ANALYSIS}}

## 7. 最终建议

{{FINAL_RECOMMENDATIONS}}"""
    
    def generate_section_content(self, section_name: str) -> str:
        """
        生成特定章节的内容
        
        Args:
            section_name: 章节名称
            
        Returns:
            生成的内容
        """
        if section_name in self.generators:
            try:
                return self.generators[section_name].generate()
            except Exception as e:
                if self.language == 'en':
                    error_msg = f"Error generating {section_name} section: {e}"
                    return f"**Generation Error**: {error_msg}"
                else:
                    error_msg = f"生成 {section_name} 章节时发生错误: {e}"
                    return f"**生成错误**: {error_msg}"
        else:
            if self.language == 'en':
                return f"**To Be Implemented**: {section_name} section not yet implemented"
            else:
                return f"**待实现**: {section_name} 章节暂未实现"
    
    def generate_case_files(self):
        """生成检查用的case文件"""
        for section_name, generator in self.generators.items():
            try:
                case_data = generator.get_case_data()
                case_file_path = os.path.join(self.output_dir, "cases", f"{section_name.lower()}_case.json")
                
                with open(case_file_path, 'w', encoding='utf-8') as f:
                    json.dump(case_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 已生成 {section_name} case文件: {case_file_path}")
            except Exception as e:
                print(f"❌ 生成 {section_name} case文件失败: {e}")
    
    def generate_report(self, 
                       generate_html: bool = True) -> Dict[str, str]:
        """
        生成完整的ES巡检报告
        
        Args:
            generate_html: 是否同时生成HTML版本
            
        Returns:
            包含markdown和html文件路径的字典
        """
        print("🚀 开始生成ES巡检报告...")
        
        # 加载模板
        template_content = self.load_template()
        
        # 替换模板中的占位符
        report_content = template_content
        
        for section_name in self.generators.keys():
            placeholder = f"{{{{{section_name}}}}}"
            if placeholder in report_content:
                print(f"📝 正在生成 {section_name} 章节...")
                section_content = self.generate_section_content(section_name)
                report_content = report_content.replace(placeholder, section_content)
        
        # 替换其他未实现的占位符
        import re
        remaining_placeholders = re.findall(r'\{\{([^}]+)\}\}', report_content)
        for placeholder in remaining_placeholders:
            full_placeholder = f"{{{{{placeholder}}}}}"
            if self.language == 'en':
                report_content = report_content.replace(full_placeholder, f"**To Be Implemented**: {placeholder} section not yet implemented")
            else:
                report_content = report_content.replace(full_placeholder, f"**待实现**: {placeholder} 章节暂未实现")
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cluster_name = "unknown"
        
        cluster_health = self.data_loader.get_cluster_health()
        if cluster_health and 'cluster_name' in cluster_health:
            cluster_name = cluster_health['cluster_name'].replace('-', '_').replace(' ', '_')
        
        report_filename = f"ES_Report_{cluster_name}_{timestamp}.md"
        report_path = os.path.join(self.output_dir, report_filename)
        
        # 保存Markdown报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        result = {"markdown": report_path}
        
        # 生成HTML版本
        if generate_html:
            try:
                print("📄 正在生成HTML版本...")
                from .html_converter import save_html_report
                html_filename = os.path.basename(report_path).replace('.md', '.html')
                html_path = os.path.join(self.output_dir, html_filename)
                
                with open(report_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                save_html_report(markdown_content, html_path)
                result["html"] = html_path
            except ImportError:
                print("⚠️ HTML转换依赖包未安装，跳过HTML生成")
            except Exception as e:
                print(f"⚠️ HTML生成失败: {e}")
        
        # 生成case文件
        print("📊 正在生成case文件...")
        self.generate_case_files()
        
        print(f"✅ 报告生成完成:")
        print(f"   📄 Markdown: {report_path}")
        if "html" in result:
            print(f"   📄 HTML: {result['html']}")
        
        return result 

class ReportGenerator:
    """
    简化的报告生成器，用于处理从ElasticsearchInspector收集的数据
    """
    
    def __init__(self):
        """初始化报告生成器"""
        pass
    
    def generate_markdown_report(self, cluster_data: Dict[str, Any]) -> str:
        """
        根据集群数据生成Markdown报告
        
        Args:
            cluster_data: 从ElasticsearchInspector.inspect_cluster()获取的数据
            
        Returns:
            Markdown格式的报告内容
        """
        
        # 获取基本信息
        inspection_time = cluster_data.get('inspection_time', datetime.now().isoformat())
        cluster_info = cluster_data.get('cluster_info', {})
        cluster_health = cluster_data.get('cluster_health', {})
        cluster_stats = cluster_data.get('cluster_stats', {})
        nodes_info = cluster_data.get('nodes_info', {})
        nodes_stats = cluster_data.get('nodes_stats', {})
        indices_info = cluster_data.get('indices_info', [])
        errors = cluster_data.get('errors', [])
        
        # 构建报告
        report = []
        
        # 标题和概述
        cluster_name = cluster_info.get('cluster_name', 'Unknown')
        es_version = cluster_info.get('version', {}).get('number', 'Unknown')
        
        report.append(f"# Elasticsearch 集群巡检报告")
        report.append(f"**集群名称**: {cluster_name}")
        report.append(f"**ES版本**: {es_version}")
        report.append(f"**巡检时间**: {inspection_time}")
        report.append("")
        
        # 执行摘要
        report.append("## 📋 执行摘要")
        
        health_status = cluster_health.get('status', 'unknown')
        status_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(health_status, "⚪")
        report.append(f"- **集群状态**: {status_emoji} {health_status.upper()}")
        
        # 节点信息
        nodes = nodes_info.get('nodes', {})
        total_nodes = len(nodes)
        report.append(f"- **节点数量**: {total_nodes}")
        
        # 索引信息
        if isinstance(indices_info, list):
            total_indices = len(indices_info)
            total_docs = sum(int(idx.get('docs.count', 0) or 0) for idx in indices_info)
            total_size = sum(self._parse_size(idx.get('store.size', '0b')) for idx in indices_info)
            
            report.append(f"- **索引数量**: {total_indices}")
            report.append(f"- **文档总数**: {total_docs:,}")
            report.append(f"- **存储大小**: {self._format_bytes(total_size)}")
        
        if errors:
            report.append(f"- **错误数量**: ⚠️ {len(errors)} 个错误")
        
        report.append("")
        
        # 集群健康详情
        report.append("## 🏥 集群健康状态")
        if cluster_health:
            report.append(f"- **状态**: {status_emoji} {health_status.upper()}")
            report.append(f"- **节点数**: {cluster_health.get('number_of_nodes', 'N/A')}")
            report.append(f"- **数据节点数**: {cluster_health.get('number_of_data_nodes', 'N/A')}")
            report.append(f"- **活跃分片**: {cluster_health.get('active_shards', 'N/A')}")
            report.append(f"- **主分片**: {cluster_health.get('active_primary_shards', 'N/A')}")
            report.append(f"- **重定位分片**: {cluster_health.get('relocating_shards', 'N/A')}")
            report.append(f"- **初始化分片**: {cluster_health.get('initializing_shards', 'N/A')}")
            report.append(f"- **未分配分片**: {cluster_health.get('unassigned_shards', 'N/A')}")
        report.append("")
        
        # 节点信息
        report.append("## 🖥️ 节点信息")
        if nodes:
            for node_id, node in nodes.items():
                node_name = node.get('name', node_id)
                node_roles = ', '.join(node.get('roles', []))
                jvm_version = node.get('jvm', {}).get('version', 'N/A')
                
                report.append(f"### {node_name}")
                report.append(f"- **节点ID**: {node_id}")
                report.append(f"- **角色**: {node_roles}")
                report.append(f"- **JVM版本**: {jvm_version}")
                report.append("")
        
        # 索引分析
        report.append("## 📊 索引分析")
        if isinstance(indices_info, list) and indices_info:
            report.append("### 索引概览")
            report.append("| 索引名称 | 状态 | 文档数 | 大小 | 分片数 |")
            report.append("|---------|------|--------|------|--------|")
            
            # 按大小排序显示前20个索引
            sorted_indices = sorted(
                indices_info[:20], 
                key=lambda x: self._parse_size(x.get('store.size', '0b')), 
                reverse=True
            )
            
            for idx in sorted_indices:
                name = idx.get('index', 'N/A')
                status = idx.get('status', 'N/A')
                docs = idx.get('docs.count', 'N/A')
                size = idx.get('store.size', 'N/A')
                shards = idx.get('pri', 'N/A')
                
                status_emoji = {"open": "🟢", "close": "🔴"}.get(status, "⚪")
                report.append(f"| {name} | {status_emoji} {status} | {docs} | {size} | {shards} |")
            
            if len(indices_info) > 20:
                report.append(f"| ... | | | | |")
                report.append(f"| *显示前20个，共{len(indices_info)}个索引* | | | | |")
        
        report.append("")
        
        # 系统资源使用
        report.append("## 💾 系统资源")
        if cluster_stats:
            nodes_stats_summary = cluster_stats.get('nodes', {})
            if nodes_stats_summary:
                # JVM内存
                jvm = nodes_stats_summary.get('jvm', {})
                if jvm:
                    heap_used = jvm.get('mem', {}).get('heap_used_in_bytes', 0)
                    heap_max = jvm.get('mem', {}).get('heap_max_in_bytes', 0)
                    heap_percent = int(heap_used * 100 / heap_max) if heap_max > 0 else 0
                    
                    report.append(f"- **JVM堆内存使用**: {heap_percent}% ({self._format_bytes(heap_used)} / {self._format_bytes(heap_max)})")
                
                # 文件系统
                fs = nodes_stats_summary.get('fs', {})
                if fs:
                    total_bytes = fs.get('total_in_bytes', 0)
                    available_bytes = fs.get('available_in_bytes', 0)
                    used_bytes = total_bytes - available_bytes
                    used_percent = int(used_bytes * 100 / total_bytes) if total_bytes > 0 else 0
                    
                    report.append(f"- **磁盘使用**: {used_percent}% ({self._format_bytes(used_bytes)} / {self._format_bytes(total_bytes)})")
        
        report.append("")
        
        # 错误和警告
        if errors:
            report.append("## ⚠️ 错误和警告")
            for error in errors:
                report.append(f"- ❌ {error}")
            report.append("")
        
        # 建议
        report.append("## 💡 建议和提醒")
        recommendations = self._generate_recommendations(cluster_data)
        for rec in recommendations:
            report.append(f"- {rec}")
        
        return '\n'.join(report)
    
    def _parse_size(self, size_str: str) -> int:
        """将大小字符串转换为字节数"""
        if not size_str or size_str == 'N/A':
            return 0
        
        size_str = size_str.lower().strip()
        
        multipliers = {
            'b': 1,
            'kb': 1024,
            'mb': 1024**2,
            'gb': 1024**3,
            'tb': 1024**4,
        }
        
        for unit, multiplier in multipliers.items():
            if size_str.endswith(unit):
                try:
                    number = float(size_str[:-len(unit)])
                    return int(number * multiplier)
                except ValueError:
                    return 0
        
        try:
            return int(float(size_str))
        except ValueError:
            return 0
    
    def _format_bytes(self, bytes_value: int) -> str:
        """格式化字节数为可读字符串"""
        if bytes_value == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while bytes_value >= 1024 and unit_index < len(units) - 1:
            bytes_value /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(bytes_value)} {units[unit_index]}"
        else:
            return f"{bytes_value:.1f} {units[unit_index]}"
    
    def _generate_recommendations(self, cluster_data: Dict[str, Any]) -> list:
        """生成建议列表"""
        recommendations = []
        
        cluster_health = cluster_data.get('cluster_health', {})
        health_status = cluster_health.get('status', 'unknown')
        
        # 健康状态建议
        if health_status == 'red':
            recommendations.append("🔴 **紧急**: 集群状态为RED，存在不可用的主分片，请立即检查")
        elif health_status == 'yellow':
            recommendations.append("🟡 **注意**: 集群状态为YELLOW，存在未分配的副本分片")
        
        # 未分配分片建议
        unassigned_shards = cluster_health.get('unassigned_shards', 0)
        if unassigned_shards > 0:
            recommendations.append(f"📊 发现 {unassigned_shards} 个未分配分片，建议检查集群容量和分片策略")
        
        # 索引数量建议
        indices_info = cluster_data.get('indices_info', [])
        if isinstance(indices_info, list) and len(indices_info) > 1000:
            recommendations.append("📈 索引数量较多（>1000），建议考虑索引生命周期管理(ILM)")
        
        # 资源使用建议
        cluster_stats = cluster_data.get('cluster_stats', {})
        nodes_stats = cluster_stats.get('nodes', {})
        if nodes_stats:
            jvm = nodes_stats.get('jvm', {})
            if jvm:
                heap_used = jvm.get('mem', {}).get('heap_used_in_bytes', 0)
                heap_max = jvm.get('mem', {}).get('heap_max_in_bytes', 0)
                heap_percent = int(heap_used * 100 / heap_max) if heap_max > 0 else 0
                
                if heap_percent > 85:
                    recommendations.append(f"🔥 JVM堆内存使用率较高({heap_percent}%)，建议监控垃圾回收情况")
                elif heap_percent > 75:
                    recommendations.append(f"⚠️ JVM堆内存使用率偏高({heap_percent}%)，建议关注")
        
        # 默认建议
        if not recommendations:
            recommendations.append("✅ 集群整体运行正常，建议定期进行巡检监控")
        
        return recommendations 