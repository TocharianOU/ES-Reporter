#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Elasticsearch 巡检工具 Web 服务启动脚本
支持命令行参数配置，优先使用 uv 包管理器
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_uv_available():
    """检查 uv 是否可用"""
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_dependencies():
    """检查项目依赖是否已安装"""
    try:
        import flask
        import reportlab
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False

def install_dependencies():
    """自动安装依赖"""
    uv_available = check_uv_available()
    
    if uv_available:
        print("🚀 检测到 uv，使用 uv 安装依赖...")
        try:
            # 尝试安装当前项目
            subprocess.run(['uv', 'pip', 'install', '-e', '.'], check=True)
            print("✅ 使用 uv 安装依赖成功")
            return True
        except subprocess.CalledProcessError:
            print("⚠️  uv 安装失败，降级到 pip")
    
    # 降级到 pip
    print("📦 使用 pip 安装依赖...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ 使用 pip 安装依赖成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip 安装也失败了")
        return False

def main():
    parser = argparse.ArgumentParser(description='Elasticsearch 集群巡检工具 Web 服务')
    
    parser.add_argument('--host', default='0.0.0.0', 
                       help='服务绑定地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, 
                       help='服务端口 (默认: 5000)')
    parser.add_argument('--debug', action='store_true', 
                       help='启用调试模式')
    parser.add_argument('--workers', type=int, default=4,
                       help='工作进程数 (生产环境使用)')
    parser.add_argument('--production', action='store_true',
                       help='生产环境模式 (使用gunicorn)')
    parser.add_argument('--auto-install', action='store_true',
                       help='自动安装缺失的依赖')
    
    args = parser.parse_args()
    
    # 检查依赖
    deps_ok = check_dependencies()
    if not deps_ok:
        if args.auto_install:
            print("🔧 自动安装依赖...")
            if not install_dependencies():
                print("❌ 依赖安装失败，请手动安装")
                print_install_instructions()
                sys.exit(1)
        else:
            print_install_instructions()
            sys.exit(1)
    
    # 显示启动信息
    uv_status = "✓ uv" if check_uv_available() else "pip"
    print("🚀 启动 Elasticsearch 巡检工具 Web 服务")
    print(f"📍 服务地址: http://{args.host}:{args.port}")
    print(f"📦 包管理器: {uv_status}")
    print("💡 功能特性:")
    print("   ✓ ES集群连接测试")
    print("   ✓ 实时巡检报告生成")  
    print("   ✓ Markdown/HTML报告下载")
    print("   ✓ 报告在线预览")
    print("   ✓ 纯Python实现，跨平台运行")
    print()
    
    if args.production:
        # 生产环境使用gunicorn
        try:
            import gunicorn
        except ImportError:
            print("❌ 生产环境需要安装gunicorn")
            if check_uv_available():
                print("请运行: uv pip install -e \".[production]\"")
            else:
                print("请运行: pip install gunicorn")
            sys.exit(1)
        
        # 使用 uv 运行 gunicorn (如果可用)
        if check_uv_available():
            cmd = ['uv', 'run', 'gunicorn', '-w', str(args.workers), '-b', f'{args.host}:{args.port}', 'app:app']
        else:
            cmd = ['gunicorn', '-w', str(args.workers), '-b', f'{args.host}:{args.port}', 'app:app']
        
        os.execvp(cmd[0], cmd)
    else:
        # 开发环境使用Flask内置服务器
        try:
            from app import app
            app.run(
                host=args.host,
                port=args.port,
                debug=args.debug,
                threaded=True
            )
        except ImportError as e:
            print(f"❌ 无法导入应用模块: {e}")
            print("请确保在项目根目录下运行此脚本")
            sys.exit(1)

def print_install_instructions():
    """打印安装说明"""
    uv_available = check_uv_available()
    
    print("\n📋 安装依赖说明:")
    if uv_available:
        print("  推荐使用 uv (更快):")
        print("    uv pip install -e .")
        print("    # 或安装开发依赖: uv pip install -e \".[dev]\"")
        print("    # 或安装生产依赖: uv pip install -e \".[production]\"")
        print("")
        print("  传统方式:")
    else:
        print("  安装 uv (推荐):")
        print("    curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("    # 然后: uv pip install -e .")
        print("")
        print("  或使用 pip:")
    
    print("    pip install -r requirements.txt")
    print("")
    print("  自动安装:")
    print("    python run_web.py --auto-install")

if __name__ == '__main__':
    main() 