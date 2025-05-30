#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文件名生成功能
"""

from datetime import datetime

def generate_download_filename(original_filename: str, report_format: str) -> str:
    """
    基于原始ZIP文件名生成下载文件名
    
    Args:
        original_filename: 原始ZIP文件名 (如: diagnostic_data.zip)
        report_format: 报告格式 ('html' 或 'md')
    
    Returns:
        生成的下载文件名 (如: diagnostic_data_report.html)
    """
    # 去掉.zip扩展名
    base_name = original_filename
    if base_name.lower().endswith('.zip'):
        base_name = base_name[:-4]
    
    # 添加时间戳和格式后缀
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_report_{timestamp}.{report_format}"

if __name__ == "__main__":
    print("🧪 测试文件名生成功能")
    
    test_cases = [
        ("diagnostic_250528.zip", "html"),
        ("diagnostic_250528.zip", "md"), 
        ("250528.zip", "html"),
        ("elasticsearch_diagnostic.zip", "md"),
        ("test.zip", "html")
    ]
    
    for original_name, format_type in test_cases:
        generated_name = generate_download_filename(original_name, format_type)
        print(f"📁 {original_name:25} → {generated_name}")
    
    print("\n✅ 测试完成！") 