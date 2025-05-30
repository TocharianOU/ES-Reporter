#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Elasticsearch 巡检工具 Web 应用
支持上传 diagnostic 文件并生成报告
"""

import os
import sys
import tempfile
import shutil
import zipfile
import uuid
import re
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入本地模块
from src.report_generator import ESReportGenerator
from src.html_converter import markdown_to_html, create_html_template
from src.i18n import detect_browser_language, i18n

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB 最大文件大小

# 全局变量存储任务状态
tasks = {}
reports = {}

# 在所有路由前添加调试信息
@app.before_request
def log_request_info():
    print(f"Request path: {request.path}")
    print(f"Request url: {request.url}")
    print(f"Request base url: {request.base_url}")

def markdown_to_html(markdown_content):
    """
    将Markdown内容转换为HTML
    简化版本，专门处理巡检报告格式
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
    
    # 处理换行和段落
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
    
    # 第一行是表头
    header_line = table_lines[0].strip()
    header_cells = [cell.strip() for cell in header_line.split('|')[1:-1]]
    
    # 第二行通常是分隔符，跳过
    data_lines = table_lines[2:] if len(table_lines) > 2 else []
    
    html = ['<table class="table table-striped table-bordered">']
    
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

@app.route('/')
def index():
    """主页 - 支持语言检测"""
    # 检测浏览器语言
    accept_language = request.headers.get('Accept-Language', '')
    detected_lang = detect_browser_language(accept_language)
    
    # 设置语言
    i18n.set_language(detected_lang)
    
    return render_template('index.html', language=detected_lang)

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Elasticsearch 巡检工具',
        'version': '2.0.0',
        'path': request.path
    })

@app.route('/api/upload-diagnostic', methods=['POST'])
def upload_diagnostic():
    """上传并处理 diagnostic 文件"""
    try:
        # 获取语言参数
        language = request.form.get('language', 'zh')  # 默认中文
        if language not in ['zh', 'en']:
            language = 'zh'
        
        # 设置国际化语言
        i18n.set_language(language)
        
        # 检查文件
        if 'diagnostic_file' not in request.files:
            return jsonify({'success': False, 'message': i18n.t('error_no_file', 'ui')})
        
        file = request.files['diagnostic_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': i18n.t('error_no_file', 'ui')})
        
        if not file.filename.lower().endswith('.zip'):
            return jsonify({'success': False, 'message': i18n.t('error_file_format', 'ui')})
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        upload_dir = os.path.join(temp_dir, 'diagnostic')
        
        try:
            # 保存上传的文件
            filename = secure_filename(file.filename)
            zip_path = os.path.join(temp_dir, filename)
            file.save(zip_path)
            
            # 解压文件
            print(f"📁 解压诊断文件: {filename}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(upload_dir)
            
            # 查找实际的数据目录
            data_dir = find_diagnostic_data_dir(upload_dir)
            if not data_dir:
                return jsonify({'success': False, 'message': i18n.t('error_invalid_diagnostic', 'ui')})
            
            print(f"📊 发现诊断数据目录: {data_dir}")
            
            # 生成报告
            print("🚀 开始生成报告...")
            report_generator = ESReportGenerator(data_dir, language=language)  # 传递语言参数
            report_result = report_generator.generate_report(generate_html=True)  # 生成HTML版本
            
            # 读取报告内容
            markdown_path = report_result.get('markdown')
            if not markdown_path or not os.path.exists(markdown_path):
                return jsonify({'success': False, 'message': i18n.t('error_report_failed', 'ui')})
            
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 转换为HTML
            html_content = markdown_to_html(markdown_content)
            
            # 生成唯一报告ID
            report_id = str(uuid.uuid4())
            
            # 保存报告数据
            reports[report_id] = {
                'markdown_content': markdown_content,
                'html_content': html_content,
                'markdown_path': markdown_path,
                'html_path': report_result.get('html'),
                'generated_at': datetime.now().isoformat(),
                'filename': filename,
                'language': language  # 保存语言信息
            }
            
            print(f"✅ 报告生成完成: {report_id}")
            
            return jsonify({
                'success': True,
                'report_id': report_id,
                'report_content': markdown_content,
                'html_content': html_content,
                'generated_at': datetime.now().isoformat(),
                'language': language
            })
            
        except zipfile.BadZipFile:
            return jsonify({'success': False, 'message': i18n.t('error_invalid_zip', 'ui')})
        except Exception as e:
            print(f"❌ 处理文件时发生错误: {e}")
            return jsonify({'success': False, 'message': f'{i18n.t("error_processing", "ui")}: {str(e)}'})
        finally:
            # 清理临时文件（保留报告文件）
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                if os.path.exists(upload_dir):
                    shutil.rmtree(upload_dir)
            except Exception as e:
                print(f"⚠️ 清理临时文件失败: {e}")
        
    except Exception as e:
        print(f"❌ 上传处理失败: {e}")
        return jsonify({'success': False, 'message': f'{i18n.t("error_server", "ui")}: {str(e)}'})

def find_diagnostic_data_dir(base_dir):
    """查找诊断数据目录"""
    # 常见的诊断数据目录结构
    possible_paths = [
        base_dir,
        os.path.join(base_dir, '*'),  # 第一级子目录
    ]
    
    # 查找包含关键文件的目录
    key_files = ['cluster_health.json', 'cluster_stats.json', 'nodes_info.json']
    
    def check_directory(dir_path):
        """检查目录是否包含诊断文件"""
        if not os.path.isdir(dir_path):
            return False
        files = os.listdir(dir_path)
        return any(key_file in files for key_file in key_files)
    
    # 直接检查基础目录
    if check_directory(base_dir):
        return base_dir
    
    # 检查子目录
    try:
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and check_directory(item_path):
                return item_path
    except Exception as e:
        print(f"⚠️ 搜索诊断目录时出错: {e}")
    
    return None

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

@app.route('/api/download-html/<report_id>')
def download_html(report_id):
    """下载HTML报告"""
    if report_id not in reports:
        return jsonify({'error': '报告不存在'}), 404
    
    report_data = reports[report_id]
    markdown_content = report_data.get('markdown_content')
    
    if not markdown_content:
        return jsonify({'error': 'HTML内容不存在'}), 404
    
    try:
        # 生成优化的HTML内容
        html_content = markdown_to_html(markdown_content)
        full_html = create_html_template(html_content, "Elasticsearch 巡检报告")
        
        # 创建临时HTML文件
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_file.write(full_html)
        temp_file.close()
        
        filename = generate_download_filename(report_data['filename'], 'html')
        
        def remove_file(response):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass
            return response
        
        response = send_file(temp_file.name, as_attachment=True, download_name=filename)
        response.call_on_close(remove_file)
        return response
    except Exception as e:
        return jsonify({'error': f'HTML下载失败: {str(e)}'}), 500

@app.route('/api/download-markdown/<report_id>')
def download_markdown(report_id):
    """下载Markdown报告"""
    if report_id not in reports:
        return jsonify({'error': '报告不存在'}), 404
    
    report_data = reports[report_id]
    markdown_path = report_data.get('markdown_path')
    
    if not markdown_path or not os.path.exists(markdown_path):
        return jsonify({'error': 'Markdown文件不存在'}), 404
    
    try:
        filename = generate_download_filename(report_data['filename'], 'md')
        return send_file(markdown_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': f'Markdown下载失败: {str(e)}'}), 500

@app.route('/api/reports')
def list_reports():
    """列出所有报告"""
    report_list = []
    for report_id, data in reports.items():
        report_list.append({
            'id': report_id,
            'generated_at': data['generated_at'],
            'filename': data['filename']
        })
    
    return jsonify({
        'success': True,
        'reports': sorted(report_list, key=lambda x: x['generated_at'], reverse=True)
    })

@app.errorhandler(413)
def too_large(e):
    """文件过大处理"""
    return jsonify({'success': False, 'message': '文件大小超过限制（最大100MB）'}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({'error': '页面不存在'}), 404

@app.errorhandler(500)
def server_error(e):
    """500错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Elasticsearch 巡检工具 Web 服务')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=5000, help='监听端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    print("🚀 启动 Elasticsearch 巡检工具 Web 服务")
    print(f"📍 服务地址: http://{args.host}:{args.port}")
    print("💡 功能特性:")
    print("   ✓ 上传 Diagnostic ZIP 文件")
    print("   ✓ 自动解析和分析")
    print("   ✓ 生成详细巡检报告")
    print("   ✓ 实时 HTML 预览")
    print("   ✓ Markdown/HTML 下载")
    print()
    
    app.run(host=args.host, port=args.port, debug=args.debug) 