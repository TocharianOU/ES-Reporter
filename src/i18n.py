"""
国际化配置模块
支持中文和英文的双语切换
"""

import os
from typing import Dict, Any

# 支持的语言列表
SUPPORTED_LANGUAGES = ['zh', 'en']
DEFAULT_LANGUAGE = 'zh'

# 翻译字典
TRANSLATIONS = {
    'zh': {
        # 前端界面翻译
        'ui': {
            'title': 'Elasticsearch 巡检工具',
            'subtitle': '上传 Diagnostic 文件，生成详细巡检报告',
            'upload_title': '上传 Diagnostic 文件',
            'drag_drop_text': '拖拽文件到此处或点击上传',
            'file_format_text': '支持 .zip 格式的 Elasticsearch Diagnostic 文件',
            'select_file_btn': '选择文件',
            'file_selected': '文件已选择',
            'generate_report_btn': '生成巡检报告',
            'download_markdown': '下载 Markdown',
            'download_html': '下载 HTML',
            'report_title': '巡检报告',
            'language_selector': '语言',
            'chinese': '中文',
            'english': 'English',
            
            # 状态提示
            'status_uploading': '正在上传文件...',
            'status_uploading_desc': '文件上传中，请稍候',
            'status_extracting': '正在解压文件...',
            'status_extracting_desc': '解压诊断文件并验证格式',
            'status_analyzing': '正在分析数据...',
            'status_analyzing_desc': '分析集群状态和配置信息',
            'status_generating': '正在生成报告...',
            'status_generating_desc': '生成详细的巡检报告',
            'status_completed': '处理完成！',
            'status_completed_desc': '报告生成成功',
            
            # 错误信息
            'error_title': '错误',
            'error_file_format': '请选择 .zip 格式的文件',
            'error_report_failed': '报告生成失败',
            'error_network': '网络错误',
            'error_download_markdown': 'Markdown 下载失败',
            'error_download_html': 'HTML 下载失败',
            'error_server_response': '服务器返回非JSON响应',
            
            # 后端API错误信息
            'error_no_file': '没有选择文件',
            'error_invalid_diagnostic': '无法找到有效的诊断数据目录',
            'error_invalid_zip': '文件不是有效的ZIP格式',
            'error_processing': '处理文件时发生错误',
            'error_server': '服务器错误',
            
            # 进度
            'progress_completed': '% 完成',
            
            # 新增UI翻译
            'upload_area_title': '上传诊断文件',
            'upload_area_desc': '拖拽您的 Elasticsearch 诊断 ZIP 文件到此处，或点击选择文件',
            'select_file': '选择文件',
            'generating_report': '正在生成报告...',
            'report_generated': '报告生成成功',
            'view_reports': '查看所有报告',
            'processing': '处理中...',
            'upload_success': '文件上传成功',
            'language_switched': '语言切换成功',
            'file_too_large': '文件大小超过限制（最大100MB）',
            'invalid_file_type': '无效文件类型，请上传ZIP文件',
            'upload_failed': '上传失败',
            'no_diagnostic_data': '上传文件中未发现有效的诊断数据',
            'report_generation_failed': '报告生成失败',
            'cluster_name': '集群名称',
            'generated_time': '生成时间',
            'report_summary': '报告摘要',
            'health_status': '健康状态',
            'node_count': '节点数量',
            'index_count': '索引数量',
            'data_size': '数据大小',
            'recommendations': '建议',
            'view_details': '查看详情',
            'refresh': '刷新',
            'clear_all': '清空全部',
            
            # 诊断指南页面
            'diagnostic_guide_title': '获取 Elasticsearch Diagnostic 包',
            'diagnostic_guide_subtitle': '简单几步，轻松生成诊断文件',
            'back_to_home': '返回主页',
            'quick_start': '快速开始',
            'step_1_title': '下载诊断工具',
            'step_1_desc': '从官方 GitHub 仓库下载最新版本的支持诊断工具',
            'step_2_title': '解压并运行',
            'step_2_desc': '解压下载的文件并运行诊断工具',
            'step_3_title': '获取诊断文件',
            'step_3_desc': '工具运行完成后，会生成一个 ZIP 格式的诊断文件',
            'generated_file_format': '生成的文件格式',
            'common_parameters': '常用参数',
            'local_mode': '本地模式',
            'remote_mode': '远程模式',
            'with_auth': '带认证',
            'api_mode': 'API模式',
            'need_more_help': '需要更多帮助？',
            'need_more_help_desc': '查看官方文档获取详细的使用说明和高级功能',
            'visit_github': '访问官方 GitHub 仓库',
            
            # 主页获取 Diagnostic 包模块
            'get_diagnostic_title': '获取 Diagnostic 包',
            'get_diagnostic_desc': '了解如何生成 Elasticsearch 诊断文件',
            'get_diagnostic_btn': '获取方法',
            
            # Terms of Use 页面
            'terms_of_use': '使用条款',
            'terms_title': 'Elasticsearch 巡检工具 - 使用条款',
            'last_updated': '最后更新',
            'acceptance_title': '条款接受',
            'acceptance_content': '通过使用本服务，您同意遵守以下使用条款。如果您不同意这些条款，请停止使用本服务。',
            'service_description_title': '服务描述',
            'service_description_content': '本工具用于分析 Elasticsearch 诊断文件并生成巡检报告。我们提供文件上传、分析和报告生成服务。',
            'data_processing_title': '数据处理与隐私',
            'data_processing_content': '我们承诺保护您的数据安全：',
            'data_processing_item1': '上传的诊断文件仅用于生成报告',
            'data_processing_item2': '我们不收集个人身份信息',
            'data_processing_item3': '所有数据传输均经过加密保护',
            'data_processing_item4': '我们可能保存匿名化的技术数据用于改进服务',
            'data_retention_title': '数据管理',
            'data_management_content': '为提高服务质量，我们可能保留匿名化的技术数据。',
            'user_rights_title': '您的权利',
            'user_rights_content': '您享有以下数据权利：',
            'user_right1': '了解我们如何处理您的数据',
            'user_right2': '要求删除您的数据',
            'user_right3': '选择退出数据收集',
            'copyright': '© 2024 Elasticsearch 巡检工具',
            'cookies_title': 'Cookies和跟踪',
            'cookies_content': '本网站使用必要的cookies来维持会话状态和语言偏好。我们不使用跟踪cookies或第三方分析服务。',
            'service_availability_title': '服务可用性',
            'service_availability_content': '我们努力保持服务的持续可用性，但不保证100%的正常运行时间。服务可能因维护或技术问题而暂时中断。',
            'liability_title': '责任限制',
            'liability_content': '本服务按"现状"提供，我们对服务的准确性、完整性或可靠性不承担责任。使用本服务的风险由您自行承担。',
            'changes_title': '条款变更',
            'changes_content': '我们保留随时修改这些条款的权利。重大变更将通过网站通知的形式提前告知用户。',
            'contact_title': '联系我们',
            'contact_content': '如果您对这些条款或数据处理有任何疑问，请联系我们：',
            'contact_email': '邮箱',
            'contact_email_address': 'luke@newmindtech.cn',
            'developer_title': '开发者',
            'developer_content': '本工具由 Luke 开发和维护。',
        },
        
        # 报告内容翻译
        'report': {
            'title': 'Elasticsearch 集群巡检报告',
            'generated_time': '报告生成时间',
            'cluster_overview': '集群概览',
            'cluster_name': '集群名称',
            'cluster_uuid': '集群UUID',
            'version': '版本信息',
            'elasticsearch_version': 'Elasticsearch版本',
            'lucene_version': 'Lucene版本',
            'jvm_version': 'JVM版本',
            'os_info': '操作系统信息',
            
            'node_information': '节点信息',
            'node_count': '节点总数',
            'master_nodes': '主节点数',
            'data_nodes': '数据节点数',
            'ingest_nodes': '摄取节点数',
            'coordinating_nodes': '协调节点数',
            
            'cluster_health': '集群健康状态',
            'health_status': '健康状态',
            'active_shards': '活跃分片数',
            'relocating_shards': '迁移中分片数',
            'initializing_shards': '初始化分片数',
            'unassigned_shards': '未分配分片数',
            'delayed_unassigned_shards': '延迟未分配分片数',
            'pending_tasks': '待处理任务数',
            
            'index_statistics': '索引统计',
            'total_indices': '索引总数',
            'total_documents': '文档总数',
            'total_size': '总存储大小',
            'index_name': '索引名称',
            'document_count': '文档数量',
            'primary_size': '主分片大小',
            'total_size_with_replicas': '总大小(含副本)',
            'shards': '分片数',
            'replicas': '副本数',
            'health': '健康状态',
            
            'configuration_analysis': '配置分析',
            'cluster_settings': '集群配置',
            'index_settings': '索引配置',
            'node_settings': '节点配置',
            
            'performance_analysis': '性能分析',
            'slow_queries': '慢查询',
            'resource_usage': '资源使用情况',
            'cpu_usage': 'CPU使用率',
            'memory_usage': '内存使用率',
            'disk_usage': '磁盘使用率',
            'heap_usage': '堆内存使用率',
            
            'recommendations': '建议与优化',
            'critical_issues': '严重问题',
            'warnings': '警告',
            'suggestions': '建议',
            
            'security_analysis': '安全分析',
            'security_enabled': '安全功能状态',
            'authentication': '认证配置',
            'authorization': '授权配置',
            'encryption': '加密配置',
            
            'backup_recovery': '备份与恢复',
            'snapshot_repositories': '快照仓库',
            'backup_policies': '备份策略',
            'recovery_status': '恢复状态',
            
            # 状态值
            'green': '绿色',
            'yellow': '黄色',
            'red': '红色',
            'enabled': '已启用',
            'disabled': '已禁用',
            'active': '活跃',
            'inactive': '非活跃',
            'unknown': '未知',
            
            # 单位
            'bytes': '字节',
            'kb': 'KB',
            'mb': 'MB',
            'gb': 'GB',
            'tb': 'TB',
            'percent': '%',
            'count': '个',
            'nodes': '节点',
            'shards': '分片',
            'documents': '文档',
            'indices': '索引'
        }
    },
    
    'en': {
        # Frontend UI translations
        'ui': {
            'title': 'Elasticsearch Inspection Tool',
            'subtitle': 'Upload Diagnostic Files to Generate Detailed Inspection Reports',
            'upload_title': 'Upload Diagnostic File',
            'drag_drop_text': 'Drag and drop files here or click to upload',
            'file_format_text': 'Supports .zip format Elasticsearch Diagnostic files',
            'select_file_btn': 'Select File',
            'file_selected': 'File Selected',
            'generate_report_btn': 'Generate Inspection Report',
            'download_markdown': 'Download Markdown',
            'download_html': 'Download HTML',
            'report_title': 'Inspection Report',
            'language_selector': 'Language',
            'chinese': '中文',
            'english': 'English',
            
            # Status messages
            'status_uploading': 'Uploading file...',
            'status_uploading_desc': 'File upload in progress, please wait',
            'status_extracting': 'Extracting file...',
            'status_extracting_desc': 'Extracting diagnostic file and validating format',
            'status_analyzing': 'Analyzing data...',
            'status_analyzing_desc': 'Analyzing cluster status and configuration',
            'status_generating': 'Generating report...',
            'status_generating_desc': 'Generating detailed inspection report',
            'status_completed': 'Process completed!',
            'status_completed_desc': 'Report generated successfully',
            
            # Error messages
            'error_title': 'Error',
            'error_file_format': 'Please select a .zip format file',
            'error_report_failed': 'Report generation failed',
            'error_network': 'Network error',
            'error_download_markdown': 'Markdown download failed',
            'error_download_html': 'HTML download failed',
            'error_server_response': 'Server returned non-JSON response',
            
            # Backend API error messages
            'error_no_file': 'No file selected',
            'error_invalid_diagnostic': 'Unable to find valid diagnostic data directory',
            'error_invalid_zip': 'File is not a valid ZIP format',
            'error_processing': 'Error occurred while processing file',
            'error_server': 'Server error',
            
            # Progress
            'progress_completed': '% completed',
            
            # UI translations
            'upload_area_title': 'Upload Diagnostic Files',
            'upload_area_desc': 'Drag and drop your Elasticsearch diagnostic ZIP file here, or click to select file',
            'select_file': 'Select File',
            'generating_report': 'Generating Report...',
            'report_generated': 'Report Generated Successfully',
            'view_reports': 'View All Reports',
            'processing': 'Processing...',
            'upload_success': 'File uploaded successfully',
            'language_switched': 'Language switched successfully',
            'file_too_large': 'File size exceeds limit (max 100MB)',
            'invalid_file_type': 'Invalid file type, please upload ZIP files',
            'upload_failed': 'Upload failed',
            'error_invalid_zip': 'Invalid ZIP file format',
            'error_processing': 'File processing error',
            'error_server': 'Server internal error',
            'no_diagnostic_data': 'No valid diagnostic data found in uploaded file',
            'report_generation_failed': 'Report generation failed',
            'cluster_name': 'Cluster Name',
            'generated_time': 'Generated Time',
            'report_summary': 'Report Summary',
            'health_status': 'Health Status',
            'node_count': 'Node Count',
            'index_count': 'Index Count',
            'data_size': 'Data Size',
            'recommendations': 'Recommendations',
            'view_details': 'View Details',
            'refresh': 'Refresh',
            'clear_all': 'Clear All',
            
            # Diagnostic Guide Page
            'diagnostic_guide_title': 'Get Elasticsearch Diagnostic Package',
            'diagnostic_guide_subtitle': 'Simple steps to easily generate diagnostic files',
            'back_to_home': 'Back to Home',
            'quick_start': 'Quick Start',
            'step_1_title': 'Download Diagnostic Tool',
            'step_1_desc': 'Download the latest version of the support diagnostic tool from the official GitHub repository',
            'step_2_title': 'Extract and Run',
            'step_2_desc': 'Extract the downloaded file and run the diagnostic tool',
            'step_3_title': 'Get Diagnostic File',
            'step_3_desc': 'After the tool completes, it will generate a ZIP format diagnostic file',
            'generated_file_format': 'Generated File Format',
            'common_parameters': 'Common Parameters',
            'local_mode': 'Local Mode',
            'remote_mode': 'Remote Mode',
            'with_auth': 'With Authentication',
            'api_mode': 'API Mode',
            'need_more_help': 'Need More Help?',
            'need_more_help_desc': 'Check the official documentation for detailed usage instructions and advanced features',
            'visit_github': 'Visit Official GitHub Repository',
            
            # Home page Get Diagnostic Package module
            'get_diagnostic_title': 'Get Diagnostic Package',
            'get_diagnostic_desc': 'Learn how to generate Elasticsearch diagnostic files',
            'get_diagnostic_btn': 'Get Methods',
            
            # Terms of Use page
            'terms_of_use': 'Terms of Use',
            'terms_title': 'Elasticsearch Inspection Tool - Terms of Use',
            'last_updated': 'Last Updated',
            'acceptance_title': 'Acceptance of Terms',
            'acceptance_content': 'By using this service, you agree to comply with the following terms of use. If you do not agree to these terms, please stop using this service.',
            'service_description_title': 'Service Description',
            'service_description_content': 'This tool is used to analyze Elasticsearch diagnostic files and generate inspection reports. We provide file upload, analysis, and report generation services.',
            'data_processing_title': 'Data Processing & Privacy',
            'data_processing_content': 'We are committed to protecting your data security:',
            'data_processing_item1': 'Uploaded diagnostic files are used only for generating reports',
            'data_processing_item2': 'We do not collect personal identification information',
            'data_processing_item3': 'All data transmission is encrypted and protected',
            'data_processing_item4': 'We may retain anonymized technical data for service improvement',
            'data_retention_title': 'Data Management',
            'data_management_content': 'To improve service quality, we may retain anonymized technical data.',
            'user_rights_title': 'Your Rights',
            'user_rights_content': 'You have the following data rights:',
            'user_right1': 'Know how we process your data',
            'user_right2': 'Request deletion of your data',
            'user_right3': 'Opt out of data collection',
            'copyright': '© 2024 Elasticsearch Inspection Tool',
            'cookies_title': 'Cookies and Tracking',
            'cookies_content': 'This website uses necessary cookies to maintain session state and language preferences. We do not use tracking cookies or third-party analytics services.',
            'service_availability_title': 'Service Availability',
            'service_availability_content': 'We strive to maintain continuous service availability, but do not guarantee 100% uptime. Service may be temporarily interrupted due to maintenance or technical issues.',
            'liability_title': 'Limitation of Liability',
            'liability_content': 'This service is provided "as is" and we accept no responsibility for the accuracy, completeness, or reliability of the service. You use this service at your own risk.',
            'changes_title': 'Changes to Terms',
            'changes_content': 'We reserve the right to modify these terms at any time. Significant changes will be notified to users in advance through website notifications.',
            'contact_title': 'Contact Us',
            'contact_content': 'If you have any questions about these terms or data processing, please contact us:',
            'contact_email': 'Email',
            'contact_email_address': 'tocharian139@protonmail.com',
            'developer_title': 'Developer',
            'developer_content': 'This tool is developed and maintained by Luke.',
        },
        
        # Report content translations
        'report': {
            'title': 'Elasticsearch Cluster Inspection Report',
            'generated_time': 'Report Generated Time',
            'cluster_overview': 'Cluster Overview',
            'cluster_name': 'Cluster Name',
            'cluster_uuid': 'Cluster UUID',
            'version': 'Version Information',
            'elasticsearch_version': 'Elasticsearch Version',
            'lucene_version': 'Lucene Version',
            'jvm_version': 'JVM Version',
            'os_info': 'Operating System Information',
            
            'node_information': 'Node Information',
            'node_count': 'Total Nodes',
            'master_nodes': 'Master Nodes',
            'data_nodes': 'Data Nodes',
            'ingest_nodes': 'Ingest Nodes',
            'coordinating_nodes': 'Coordinating Nodes',
            
            'cluster_health': 'Cluster Health',
            'health_status': 'Health Status',
            'active_shards': 'Active Shards',
            'relocating_shards': 'Relocating Shards',
            'initializing_shards': 'Initializing Shards',
            'unassigned_shards': 'Unassigned Shards',
            'delayed_unassigned_shards': 'Delayed Unassigned Shards',
            'pending_tasks': 'Pending Tasks',
            
            'index_statistics': 'Index Statistics',
            'total_indices': 'Total Indices',
            'total_documents': 'Total Documents',
            'total_size': 'Total Storage Size',
            'index_name': 'Index Name',
            'document_count': 'Document Count',
            'primary_size': 'Primary Shard Size',
            'total_size_with_replicas': 'Total Size (with replicas)',
            'shards': 'Shards',
            'replicas': 'Replicas',
            'health': 'Health',
            
            'configuration_analysis': 'Configuration Analysis',
            'cluster_settings': 'Cluster Settings',
            'index_settings': 'Index Settings',
            'node_settings': 'Node Settings',
            
            'performance_analysis': 'Performance Analysis',
            'slow_queries': 'Slow Queries',
            'resource_usage': 'Resource Usage',
            'cpu_usage': 'CPU Usage',
            'memory_usage': 'Memory Usage',
            'disk_usage': 'Disk Usage',
            'heap_usage': 'Heap Memory Usage',
            
            'recommendations': 'Recommendations & Optimizations',
            'critical_issues': 'Critical Issues',
            'warnings': 'Warnings',
            'suggestions': 'Suggestions',
            
            'security_analysis': 'Security Analysis',
            'security_enabled': 'Security Features Status',
            'authentication': 'Authentication Configuration',
            'authorization': 'Authorization Configuration',
            'encryption': 'Encryption Configuration',
            
            'backup_recovery': 'Backup & Recovery',
            'snapshot_repositories': 'Snapshot Repositories',
            'backup_policies': 'Backup Policies',
            'recovery_status': 'Recovery Status',
            
            # New sections for detailed report
            'node_overview_table': 'Node Overview Table',
            'hardware_resources': 'Hardware Resources',
            'cpu_resources_overview': 'CPU Resources Overview', 
            'memory_resources_overview': 'Memory Resources Overview',
            'jvm_environment': 'JVM Runtime Environment',
            'jvm_version_config': 'JVM Version & Configuration',
            'gc_performance_stats': 'GC Performance Statistics',
            'node_roles_config': 'Node Roles & Configuration',
            'node_role_details': 'Node Role Assignment Details',
            'performance_metrics': 'Performance Metrics',
            'indexing_operations_stats': 'Indexing Operations Statistics',
            'storage_shard_distribution': 'Storage & Shard Distribution',
            'node_storage_usage': 'Node Storage Usage',
            'alerts_recommendations': 'Alerts & Recommendations',
            'resource_alerts_check': 'Resource Alerts Check',
            'optimization_suggestions': 'Optimization Suggestions',
            
            # Index Analysis
            'index_overview_stats': 'Index Overview Statistics',
            'basic_statistics': 'Basic Statistics',
            'average_distribution_stats': 'Average Distribution Statistics',
            'shard_health_status': 'Shard Health Status',
            'index_details_table': 'Index Details Table',
            'typical_indices_info': 'Typical Index Information (Top 20 Representative Indices)',
            'index_health_analysis': 'Index Health Status Analysis',
            'index_status_distribution': 'Index Status Distribution',
            'problem_shards_details': 'Problem Shards Details',
            'index_patterns_distribution': 'Index Patterns & Distribution',
            'index_naming_patterns': 'Index Naming Pattern Analysis',
            'shard_distribution_analysis': 'Shard Distribution Analysis',
            'node_shard_distribution': 'Node-wise Shard Distribution',
            'shard_size_distribution': 'Shard Size Distribution',
            'index_performance_metrics': 'Index Performance Metrics',
            'query_cache_performance': 'Query Cache Performance',
            'index_optimization_recommendations': 'Index Optimization Recommendations',
            'discovered_config_issues': 'Discovered Configuration Issues',
            'best_practices': 'Index Configuration Best Practices',
            'performance_optimization_suggestions': 'Performance Optimization Suggestions',
            
            # Log Analysis
            'log_file_overview': 'Log File Overview',
            'log_file_stats': 'Log File Statistics',
            'log_file_details': 'Log File Details',
            'error_log_analysis': 'Error Log Analysis',
            'error_statistics': 'Error Statistics',
            'important_error_details': 'Important Error Details',
            'warning_analysis': 'Warning Information Analysis',
            'warning_statistics': 'Warning Statistics',
            'high_frequency_warning_analysis': 'High-frequency Warning Analysis',
            'log_accumulation_analysis': 'Log Accumulation Analysis',
            'accumulation_stats': 'Accumulation Statistics',
            'important_events_analysis': 'Important Events Analysis',
            'important_events_overview': 'Important Events Overview',
            
            # Final Recommendations
            'cluster_health_assessment': 'Cluster Health Assessment',
            'business_confirmation_items': 'Items Requiring Business Confirmation',
            'overall_assessment': 'Overall Assessment',
            'core_indicators': 'Core Indicators',
            'node_resource_status': 'Node Resource Status',
            'log_health_status': 'Log Health Status',
            'implementation_principles': 'Optimization Implementation Principles',
            
            # Status values
            'green': 'Green',
            'yellow': 'Yellow',
            'red': 'Red',
            'enabled': 'Enabled',
            'disabled': 'Disabled',
            'active': 'Active',
            'inactive': 'Inactive',
            'unknown': 'Unknown',
            'normal': 'Normal',
            'high': 'High',
            'moderate': 'Moderate',
            'low': 'Low',
            
            # Common terms
            'node_name': 'Node Name',
            'ip_address': 'IP Address',
            'role': 'Role',
            'es_version': 'ES Version',
            'uptime': 'Uptime',
            'status': 'Status',
            'no_data': 'No data',
            'to_be_filled': 'To be filled',
            'days': 'days',
            'count': 'count',
            'size': 'Size',
            'type': 'Type',
            'current_log': 'Current Log',
            'compressed_log': 'Compressed Log',
            'file_name': 'File Name',
            'modified_time': 'Modified Time',
            'item': 'Item',
            'content': 'Content',
            'description': 'Description',
            'example': 'Example',
            'priority': 'Priority',
            'current_status': 'Current Status',
            'possible_reason': 'Possible Reason',
            'suggested_action': 'Suggested Action',
            'impact': 'Impact',
            'urgency': 'Urgency',
            'implementation_timing': 'Implementation Timing',
            
            # Units
            'bytes': 'Bytes',
            'kb': 'KB',
            'mb': 'MB',
            'gb': 'GB',
            'tb': 'TB',
            'percent': '%',
            'nodes': 'nodes',
            'shards': 'shards',
            'documents': 'documents',
            'indices': 'indices',
            'files': 'files'
        }
    }
}

class I18n:
    """国际化类"""
    
    def __init__(self, language: str = None):
        self.language = language or DEFAULT_LANGUAGE
        if self.language not in SUPPORTED_LANGUAGES:
            self.language = DEFAULT_LANGUAGE
    
    def set_language(self, language: str):
        """设置语言"""
        if language in SUPPORTED_LANGUAGES:
            self.language = language
    
    def get_language(self) -> str:
        """获取当前语言"""
        return self.language
    
    def t(self, key: str, category: str = 'ui', **kwargs) -> str:
        """
        翻译函数
        
        Args:
            key: 翻译键
            category: 分类 (ui, report)
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        try:
            translation = TRANSLATIONS[self.language][category][key]
            if kwargs:
                return translation.format(**kwargs)
            return translation
        except KeyError:
            # 如果找不到翻译，返回英文版本或原键
            try:
                fallback = TRANSLATIONS['en'][category][key]
                if kwargs:
                    return fallback.format(**kwargs)
                return fallback
            except KeyError:
                return key
    
    def get_translations(self, category: str = 'ui') -> Dict[str, str]:
        """获取指定分类的所有翻译"""
        try:
            return TRANSLATIONS[self.language][category]
        except KeyError:
            return TRANSLATIONS[DEFAULT_LANGUAGE][category]
    
    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        return SUPPORTED_LANGUAGES

# 全局实例
i18n = I18n()

def detect_browser_language(accept_language: str = None) -> str:
    """
    检测浏览器语言
    
    Args:
        accept_language: HTTP Accept-Language 头
        
    Returns:
        检测到的语言代码
    """
    if not accept_language:
        return DEFAULT_LANGUAGE
    
    # 解析 Accept-Language 头
    languages = []
    for lang in accept_language.split(','):
        parts = lang.strip().split(';')
        lang_code = parts[0].strip().lower()
        
        # 提取主要语言代码
        if '-' in lang_code:
            lang_code = lang_code.split('-')[0]
        
        if lang_code in ['zh', 'cn']:
            return 'zh'
        elif lang_code in ['en']:
            return 'en'
    
    return DEFAULT_LANGUAGE 