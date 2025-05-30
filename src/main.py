#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Elasticsearch 巡检工具命令行入口
支持Markdown和HTML报告生成
"""

import os
import sys
import argparse
from datetime import datetime

from es_inspector import ElasticsearchInspector
from report_generator import ESReportGenerator

def main():
    """
    命令行工具主入口
    
    示例:
    # 生成Markdown报告
    python -m src.main --data-dir ./diagnostic-data
    
    # 同时生成HTML报告
    python -m src.main --data-dir ./diagnostic-data --format both
    """
    
    parser = argparse.ArgumentParser(
        description="Elasticsearch 巡检工具 - 生成详细的集群巡检报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --data-dir ./local-diagnostics-20250528-142459
  %(prog)s --data-dir ./diagnostic-data --format html
  %(prog)s --data-dir ./diagnostic-data --output-dir ./reports
        """
    )
    
    parser.add_argument('--data-dir', 
                       required=True,
                       help='诊断数据目录路径')
    
    parser.add_argument('--output-dir', 
                       default='output',
                       help='报告输出目录 (默认: output)')
    
    parser.add_argument('--format', 
                       choices=['markdown', 'html', 'both'],
                       default='markdown',
                       help='报告格式 (默认: markdown)')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='显示详细输出')
    
    args = parser.parse_args()
    
    # 检查数据目录
    if not os.path.exists(args.data_dir):
        print(f"❌ 错误: 数据目录不存在: {args.data_dir}")
        sys.exit(1)
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("🔍 Elasticsearch 巡检工具")
    print("="*60)
    print(f"📁 数据目录: {args.data_dir}")
    print(f"📄 输出目录: {args.output_dir}")
    print(f"📋 生成格式: {args.format}")
    print("="*60)
    
    try:
        # 创建报告生成器
        generator = ESReportGenerator(args.data_dir, args.output_dir)
        
        # 确定是否生成HTML
        generate_html = args.format in ['html', 'both']
        
        print("🚀 开始生成报告...")
        result = generator.generate_report(generate_html=generate_html)
        
        print("\n✅ 报告生成完成!")
        print(f"📄 Markdown: {result['markdown']}")
        
        if 'html' in result:
            print(f"🌐 HTML: {result['html']}")
        
        print(f"\n💡 报告已保存到: {args.output_dir}")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 