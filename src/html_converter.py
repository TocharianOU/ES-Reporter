#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML转换器
将Markdown报告转换为优化的HTML格式，支持Web显示和打印
"""

import os
import re
from datetime import datetime

def markdown_to_html(markdown_content):
    """
    将Markdown内容转换为HTML
    优化显示效果和表格处理
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
    
    # 表格处理
    lines = html.split('\n')
    result_lines = []
    in_table = False
    table_buffer = []
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                in_table = True
                table_buffer = []
            table_buffer.append(line)
        else:
            if in_table:
                html_table = process_table(table_buffer)
                result_lines.append(html_table)
                in_table = False
                table_buffer = []
            
            # 处理列表
            if stripped.startswith('- '):
                if result_lines and not result_lines[-1].strip().startswith('<li>'):
                    result_lines.append('<ul>')
                
                list_content = stripped[2:].strip()
                result_lines.append(f'<li>{list_content}</li>')
            else:
                if result_lines and result_lines[-1].strip().startswith('<li>'):
                    result_lines.append('</ul>')
                
                result_lines.append(line)
    
    # 处理最后的表格和列表
    if in_table and table_buffer:
        html_table = process_table(table_buffer)
        result_lines.append(html_table)
    
    if result_lines and result_lines[-1].strip().startswith('<li>'):
        result_lines.append('</ul>')
    
    html = '\n'.join(result_lines)
    
    # 简单的段落处理
    html = html.replace('\n\n', '</p><p>')
    html = '<p>' + html + '</p>'
    html = html.replace('<p><h', '<h').replace('</h1></p>', '</h1>')
    html = html.replace('</h2></p>', '</h2>').replace('</h3></p>', '</h3>')
    html = html.replace('<p><table', '<table').replace('</table></p>', '</table>')
    html = html.replace('<p><ul>', '<ul>').replace('</ul></p>', '</ul>')
    html = html.replace('<p></p>', '')
    
    return html

def process_table(table_lines):
    """处理表格转换"""
    if len(table_lines) < 2:
        return '\n'.join(table_lines)
    
    header_line = table_lines[0].strip()
    header_cells = [cell.strip() for cell in header_line.split('|')[1:-1]]
    data_lines = table_lines[2:] if len(table_lines) > 2 else []
    
    html = ['<table>']
    
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

def create_html_template(content, title="Elasticsearch 巡检报告"):
    """
    创建完整的HTML模板
    优化Web显示和打印样式
    """
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* 通用样式 */
        body {{
            font-family: 'Microsoft YaHei', 'SimHei', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            text-align: left;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
            background: white;
        }}
        
        /* 标题样式 */
        h1 {{
            color: #2c3e50;
            font-size: 24px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 8px;
            margin: 30px 0 20px 0;
            text-align: left;
        }}
        
        h2 {{
            color: #34495e;
            font-size: 20px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
            margin: 25px 0 15px 0;
            text-align: left;
        }}
        
        h3 {{
            color: #2c3e50;
            font-size: 16px;
            margin: 20px 0 10px 0;
            text-align: left;
        }}
        
        /* 表格样式 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 12px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        table th,
        table td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
            vertical-align: top;
            word-wrap: break-word;
        }}
        
        table th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            font-size: 13px;
        }}
        
        table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        /* 表格内容优化 */
        table td:first-child {{
            font-weight: 500;
            background-color: #f8f9fa;
            width: 200px;
        }}
        
        /* 列表样式 */
        ul, ol {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        li {{
            margin: 5px 0;
            line-height: 1.5;
        }}
        
        /* 文本样式 */
        strong {{
            font-weight: bold;
            color: #2c3e50;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', Consolas, monospace;
            font-size: 12px;
            color: #c7254e;
            border: 1px solid #e1e1e8;
        }}
        
        p {{
            margin: 10px 0;
            text-align: left;
            line-height: 1.6;
        }}
        
        /* 打印样式 */
        @media print {{
            body {{
                font-size: 12px;
                line-height: 1.4;
            }}
            
            .container {{
                max-width: none;
                margin: 0;
                padding: 0;
            }}
            
            h1 {{
                font-size: 18px;
                page-break-after: avoid;
            }}
            
            h2 {{
                font-size: 16px;
                page-break-after: avoid;
            }}
            
            h3 {{
                font-size: 14px;
                page-break-after: avoid;
            }}
            
            table {{
                font-size: 10px;
                page-break-inside: avoid;
            }}
            
            table th,
            table td {{
                padding: 4px 6px;
            }}
            
            tr {{
                page-break-inside: avoid;
            }}
        }}
        
        /* Web显示优化 */
        @media screen {{
            body {{
                background-color: #f5f5f5;
            }}
            
            .container {{
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 20px auto;
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

def save_html_report(markdown_content, output_path, title="Elasticsearch 巡检报告"):
    """
    保存HTML报告到文件
    
    Args:
        markdown_content: Markdown内容
        output_path: 输出文件路径
        title: 报告标题
        
    Returns:
        生成的HTML文件路径
    """
    try:
        # 转换为HTML
        html_content = markdown_to_html(markdown_content)
        
        # 创建完整HTML
        full_html = create_html_template(html_content, title)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ HTML报告已保存: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ HTML报告保存失败: {e}")
        raise e

if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        markdown_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "report.html"
        
        if os.path.exists(markdown_file):
            try:
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                html_path = save_html_report(markdown_content, output_file)
                print(f"🎉 转换完成: {html_path}")
            except Exception as e:
                print(f"💥 转换失败: {e}")
        else:
            print(f"❌ 文件不存在: {markdown_file}")
    else:
        print("用法: python html_converter.py <markdown_file> [output_file]")