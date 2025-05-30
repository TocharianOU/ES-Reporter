#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML转换功能测试
测试Markdown到HTML的转换效果
"""

import os
import sys
import time
from pathlib import Path

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from html_converter import markdown_to_html, create_html_template, save_html_report

def find_existing_markdown_files():
    """查找现有的markdown文件"""
    markdown_files = []
    
    # 在当前目录及子目录查找markdown文件
    for root, dirs, files in os.walk('.'):
        # 跳过虚拟环境和git目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    
    return markdown_files

def test_html_conversion():
    """测试HTML转换功能"""
    
    print("🔍 查找现有的Markdown文件...")
    markdown_files = find_existing_markdown_files()
    
    if not markdown_files:
        print("❌ 没有找到任何Markdown文件")
        return False
    
    print(f"📋 找到 {len(markdown_files)} 个Markdown文件:")
    for i, file in enumerate(markdown_files, 1):
        size = os.path.getsize(file) if os.path.exists(file) else 0
        print(f"  {i}. {file} ({size} bytes)")
    
    # 选择最大的文件进行测试（通常是完整的报告）
    largest_file = max(markdown_files, key=lambda f: os.path.getsize(f) if os.path.exists(f) else 0)
    test_file = largest_file
    
    print(f"\n🎯 选择测试文件: {test_file}")
    
    # 确保输出目录存在
    output_dir = "html_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 输出目录: {output_dir}")
    
    try:
        print("\n" + "="*60)
        print("🚀 开始HTML转换测试...")
        print("="*60)
        
        start_time = time.time()
        
        # 读取Markdown内容
        with open(test_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 执行转换
        output_file = os.path.join(output_dir, "test_report.html")
        html_path = save_html_report(markdown_content, output_file, "测试报告")
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        print("="*60)
        print("🎉 HTML转换测试完成!")
        print("="*60)
        
        # 显示结果统计
        if os.path.exists(html_path):
            html_size = os.path.getsize(html_path)
            markdown_size = os.path.getsize(test_file)
            
            print(f"📊 转换统计:")
            print(f"  • 输入文件: {test_file}")
            print(f"  • 输出文件: {html_path}")
            print(f"  • Markdown大小: {markdown_size:,} bytes")
            print(f"  • HTML大小: {html_size:,} bytes")
            print(f"  • 转换耗时: {conversion_time:.2f} 秒")
            print(f"  • 大小比例: {html_size/markdown_size:.2f}x")
            
            print(f"\n💡 你可以打开HTML文件查看效果:")
            print(f"   open {html_path}")
            
            return True
        else:
            print("❌ HTML文件未能成功生成")
            return False
            
    except Exception as e:
        print(f"💥 HTML转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_conversion():
    """测试简单转换功能"""
    
    print("\n" + "="*60)
    print("🔍 简单转换测试")
    print("="*60)
    
    # 创建一个简单的测试markdown
    test_markdown = """# 测试报告

## 概述
这是一个 **测试** 报告，包含各种 *格式* 元素。

### 表格测试
| 名称 | 值 | 状态 |
|------|-----|------|
| 节点1 | 100% | 正常 |
| 节点2 | 95% | 警告 |
| 节点3 | 80% | 异常 |

### 列表测试
- 项目一：重要功能
- 项目二：性能优化
- 项目三：bug修复

### 代码测试
这是一个 `inline code` 示例。

**结论**: 测试完成，所有功能正常。
"""
    
    try:
        # 转换为HTML
        html_content = markdown_to_html(test_markdown)
        full_html = create_html_template(html_content, "简单测试报告")
        
        # 保存HTML文件
        output_dir = "html_test_output"
        os.makedirs(output_dir, exist_ok=True)
        html_path = os.path.join(output_dir, "simple_test.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ 简单测试HTML文件已生成: {html_path}")
        print(f"💡 你可以在浏览器中查看: open {html_path}")
        
        # 显示统计
        html_size = len(full_html)
        markdown_size = len(test_markdown)
        print(f"📊 大小对比: Markdown {markdown_size} bytes → HTML {html_size} bytes ({html_size/markdown_size:.1f}x)")
        
        return True
        
    except Exception as e:
        print(f"❌ 简单转换测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 HTML转换器测试")
    print("="*60)
    
    # 测试简单转换
    simple_success = test_simple_conversion()
    
    # 测试完整文件转换
    full_success = test_html_conversion()
    
    print("\n" + "="*60)
    print("📋 测试总结")
    print("="*60)
    print(f"简单转换: {'✅ 成功' if simple_success else '❌ 失败'}")
    print(f"完整转换: {'✅ 成功' if full_success else '❌ 失败'}")
    
    if simple_success and full_success:
        print("\n🎊 所有测试通过！HTML转换功能工作正常。")
        print("💡 你现在可以在Web界面中上传ZIP文件并下载HTML报告。")
    else:
        print("\n⚠️  有测试失败，请检查错误信息。") 