#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
巡检工具简单示例
"""

import os
from src.report_generator import ESReportGenerator

def main():
    """主函数"""
    
    # 检查示例数据目录是否存在
    data_dir = "local-diagnostics-20250528-142459"
    
    if not os.path.exists(data_dir):
        print("❌ 示例数据目录不存在")
        print("💡 请先上传诊断文件或使用Web界面")
        return
    
    print("🚀 开始生成ES巡检报告...")
    print(f"📁 数据目录: {data_dir}")
    
    # 创建报告生成器
    generator = ESReportGenerator(data_dir)
    
    # 生成报告（同时生成Markdown和HTML）
    result = generator.generate_report(generate_html=True)
    
    print("\n✅ 报告生成完成！")
    print(f"📄 Markdown报告: {result['markdown']}")
    
    if 'html' in result:
        print(f"📄 HTML报告: {result['html']}")
    
    print("\n💡 你现在可以:")
    print("   1. 查看Markdown报告进行编辑")
    print("   2. 打开HTML报告在浏览器中查看")
    print("   3. 使用Web界面上传更多文件")

if __name__ == "__main__":
    main()
