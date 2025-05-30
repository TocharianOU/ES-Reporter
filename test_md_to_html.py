#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Markdown到HTML转换功能
"""

import os
import sys
import traceback
import re
from pathlib import Path

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def markdown_to_html(markdown_content):
    """
    将Markdown内容转换为HTML
    这是一个简化版本，专门处理我们报告中的格式
    """
    html = markdown_content
    
    # 转义HTML特殊字符
    html = html.replace('&', '&amp;')
    html = html.replace('<', '&lt;')
    html = html.replace('>', '&gt;')
    
    # 标题处理
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # 粗体和强调
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # 代码块处理
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # 链接处理
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # 表格处理（更完善）
    lines = html.split('\n')
    result_lines = []
    in_table = False
    table_buffer = []
    
    for line in lines:
        stripped = line.strip()
        
        # 检查是否是表格行
        if stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                in_table = True
                table_buffer = []
            table_buffer.append(line)
        else:
            # 如果之前在表格中，现在退出表格
            if in_table:
                html_table = process_table(table_buffer)
                result_lines.append(html_table)
                in_table = False
                table_buffer = []
            
            # 处理列表
            if stripped.startswith('- '):
                # 如果前一行不是列表项，开始新的列表
                if result_lines and not result_lines[-1].strip().startswith('<li>'):
                    result_lines.append('<ul>')
                
                list_content = stripped[2:].strip()
                result_lines.append(f'<li>{list_content}</li>')
                
                # 检查下一行是否还是列表项，如果不是则关闭列表
                # 这里简化处理，在后面统一处理
            else:
                # 如果前一行是列表项，关闭列表
                if result_lines and result_lines[-1].strip().startswith('<li>'):
                    result_lines.append('</ul>')
                
                result_lines.append(line)
    
    # 处理最后的表格
    if in_table and table_buffer:
        html_table = process_table(table_buffer)
        result_lines.append(html_table)
    
    # 处理最后的列表
    if result_lines and result_lines[-1].strip().startswith('<li>'):
        result_lines.append('</ul>')
    
    html = '\n'.join(result_lines)
    
    # 段落处理（将连续的非HTML行包装为段落）
    html = process_paragraphs(html)
    
    return html

def process_table(table_lines):
    """处理表格转换"""
    if len(table_lines) < 2:
        return '\n'.join(table_lines)
    
    # 第一行是表头
    header_line = table_lines[0].strip()
    header_cells = [cell.strip() for cell in header_line.split('|')[1:-1]]
    
    # 第二行通常是分隔符，跳过
    data_lines = table_lines[2:] if len(table_lines) > 2 else []
    
    html = ['<table class="report-table">']
    
    # 表头
    if header_cells:
        html.append('<thead>')
        html.append('<tr>')
        for cell in header_cells:
            html.append(f'<th>{cell}</th>')
        html.append('</tr>')
        html.append('</thead>')
    
    # 表体
    if data_lines:
        html.append('<tbody>')
        for line in data_lines:
            line = line.strip()
            if line.startswith('|') and line.endswith('|'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                html.append('<tr>')
                for cell in cells:
                    html.append(f'<td>{cell}</td>')
                html.append('</tr>')
        html.append('</tbody>')
    
    html.append('</table>')
    return '\n'.join(html)

def process_paragraphs(html):
    """处理段落"""
    lines = html.split('\n')
    result = []
    in_paragraph = False
    
    for line in lines:
        stripped = line.strip()
        
        # 如果是HTML标签行或空行，不处理为段落
        if (stripped.startswith('<') or 
            stripped == '' or 
            stripped.startswith('#') or
            stripped.startswith('|')):
            
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
        else:
            # 普通文本行
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)
    
    if in_paragraph:
        result.append('</p>')
    
    return '\n'.join(result)

def create_html_template(content, title="Elasticsearch 巡检报告"):
    """创建完整的HTML页面"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 2.2em;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 1.8em;
        }}
        
        h3 {{
            color: #2c3e50;
            margin-top: 25px;
            font-size: 1.4em;
        }}
        
        .report-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        
        .report-table th,
        .report-table td {{
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: left;
            font-size: 14px;
        }}
        
        .report-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .report-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        .report-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        ul {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        
        code {{
            background: #f1f2f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
        }}
        
        p {{
            margin: 15px 0;
            text-align: justify;
        }}
        
        /* 状态指示器 */
        .status-green {{ color: #27ae60; }}
        .status-yellow {{ color: #f39c12; }}
        .status-red {{ color: #e74c3c; }}
        
        /* 表格中的数字右对齐 */
        .report-table td:last-child {{
            text-align: right;
        }}
        
        /* 打印样式 */
        @media print {{
            body {{ 
                background: white; 
                font-size: 12px;
            }}
            .container {{ 
                box-shadow: none; 
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""

def test_md_to_html():
    """测试Markdown到HTML转换"""
    
    # 查找最新的Markdown报告
    output_dir = "output"
    if not os.path.exists(output_dir):
        print("❌ 输出目录不存在")
        return False
    
    # 找到最新的Markdown文件
    md_files = [f for f in os.listdir(output_dir) if f.endswith('.md')]
    if not md_files:
        print("❌ 没有找到Markdown报告文件")
        return False
    
    # 取最新的文件
    latest_md = max(md_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
    md_path = os.path.join(output_dir, latest_md)
    
    print(f"📄 使用Markdown文件: {md_path}")
    
    try:
        # 读取Markdown内容
        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"📊 Markdown文件大小: {len(markdown_content)} 字符")
        
        # 转换为HTML
        print("🔄 开始转换为HTML...")
        html_content = markdown_to_html(markdown_content)
        
        # 创建完整的HTML页面
        full_html = create_html_template(html_content)
        
        # 保存HTML文件
        html_filename = latest_md.replace('.md', '.html')
        html_path = os.path.join(output_dir, html_filename)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ HTML文件生成成功: {html_path}")
        print(f"📊 HTML文件大小: {len(full_html)} 字符")
        
        # 显示一些统计信息
        table_count = html_content.count('<table')
        h2_count = html_content.count('<h2>')
        h3_count = html_content.count('<h3>')
        
        print(f"📈 内容统计:")
        print(f"   - 二级标题: {h2_count} 个")
        print(f"   - 三级标题: {h3_count} 个") 
        print(f"   - 表格: {table_count} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML转换失败: {e}")
        print("\n🔍 详细错误信息:")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🧪 开始测试Markdown到HTML转换")
    print("=" * 60)
    
    success = test_md_to_html()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ HTML转换测试通过")
        print("💡 提示: 可以在浏览器中打开生成的HTML文件查看效果")
    else:
        print("\n" + "=" * 60)
        print("❌ HTML转换测试失败")

if __name__ == '__main__':
    main() 