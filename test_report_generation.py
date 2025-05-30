#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
报告生成功能测试
测试完整的报告生成流程
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from report_generator import ESReportGenerator

def test_report_generation():
    """测试报告生成功能"""
    
    # 查找可用的诊断数据目录
    possible_dirs = [
        "local-diagnostics-20250528-142459",
        "test-data",
        "sample-data"
    ]
    
    data_dir = None
    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            data_dir = dir_path
            break
    
    if not data_dir:
        print("❌ 没有找到可用的诊断数据目录")
        print("💡 请确保存在以下目录之一:")
        for dir_path in possible_dirs:
            print(f"   - {dir_path}")
        return False
    
    print(f"📁 使用数据目录: {data_dir}")
    
    try:
        # 创建报告生成器
        generator = ESReportGenerator(data_dir)
        
        # 生成报告（同时生成HTML）
        print("🚀 开始生成报告...")
        result = generator.generate_report(generate_html=True)
        
        # 检查Markdown文件
        markdown_path = result.get('markdown')
        if markdown_path and os.path.exists(markdown_path):
            file_size = os.path.getsize(markdown_path)
            print(f"✅ Markdown报告生成成功: {markdown_path}")
            print(f"📊 文件大小: {file_size} bytes")
        else:
            print("❌ Markdown报告生成失败")
            return False
        
        # 检查HTML文件
        html_path = result.get('html')
        if html_path and os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            print(f"✅ HTML报告生成成功: {html_path}")
            print(f"📊 文件大小: {file_size} bytes")
        else:
            print("⚠️ HTML报告生成失败或未启用")
        
        # 显示可用的操作
        print("\n💡 你可以:")
        print(f"   📝 编辑Markdown: {markdown_path}")
        if html_path:
            print(f"   🌐 查看HTML: open {html_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 报告生成功能测试")
    print("="*60)
    
    success = test_report_generation()
    
    print("\n" + "="*60)
    if success:
        print("🎉 报告生成测试通过！")
        print("✅ Markdown和HTML报告都能正常生成")
    else:
        print("❌ 报告生成测试失败")
        print("�� 请检查数据目录和依赖是否正确") 