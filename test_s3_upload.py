#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
S3上传功能测试脚本
测试S3上传器的各项功能
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.s3_uploader import S3Uploader

def create_test_files():
    """创建测试文件"""
    temp_dir = tempfile.mkdtemp()
    print(f"📁 创建测试目录: {temp_dir}")
    
    # 创建测试ZIP文件
    zip_file = os.path.join(temp_dir, "test_diagnostic.zip")
    with open(zip_file, 'w') as f:
        f.write("这是一个测试ZIP文件内容")
    
    # 创建测试Markdown文件
    md_file = os.path.join(temp_dir, "test_report.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("""# 测试报告

## 概述
这是一个测试报告文件。

## 详细信息
- 测试时间: {time}
- 测试文件: test_diagnostic.zip

## 结论
测试完成。
""".format(time=time.strftime('%Y-%m-%d %H:%M:%S')))
    
    # 创建测试HTML文件
    html_file = os.path.join(temp_dir, "test_report.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>测试报告</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>测试报告</h1>
    <h2>概述</h2>
    <p>这是一个测试报告文件。</p>
    
    <h2>详细信息</h2>
    <ul>
        <li>测试时间: {time}</li>
        <li>测试文件: test_diagnostic.zip</li>
    </ul>
    
    <h2>结论</h2>
    <p>测试完成。</p>
</body>
</html>""".format(time=time.strftime('%Y-%m-%d %H:%M:%S')))
    
    return temp_dir, zip_file, md_file, html_file

def test_s3_configuration():
    """测试S3配置"""
    print("\n🔧 测试S3配置...")
    
    # 测试环境变量配置
    s3_uploader = S3Uploader()
    
    print(f"桶名: {s3_uploader.bucket_name}")
    print(f"区域: {s3_uploader.region}")
    print(f"已配置: {s3_uploader.is_configured()}")
    
    if not s3_uploader.is_configured():
        print("⚠️ S3未配置，请设置以下环境变量:")
        print("  - AWS_S3_BUCKET_NAME")
        print("  - AWS_ACCESS_KEY_ID")
        print("  - AWS_SECRET_ACCESS_KEY")
        print("  - AWS_REGION (可选，默认us-east-1)")
        return False
    
    return True

def test_s3_connection():
    """测试S3连接"""
    print("\n🔗 测试S3连接...")
    
    s3_uploader = S3Uploader()
    result = s3_uploader.test_connection()
    
    print(f"连接结果: {result}")
    
    if result['success']:
        print("✅ S3连接测试成功")
        return True
    else:
        print(f"❌ S3连接测试失败: {result['message']}")
        return False

def test_timestamp_folder():
    """测试Unix时间戳文件夹生成"""
    print("\n⏰ 测试Unix时间戳文件夹生成...")
    
    s3_uploader = S3Uploader()
    folder_name = s3_uploader.create_folder_with_timestamp()
    
    print(f"生成的文件夹名: {folder_name}")
    
    # 验证是否为有效的Unix时间戳
    try:
        timestamp = int(folder_name)
        if timestamp > 0:
            print("✅ 时间戳格式正确")
            return True
        else:
            print("❌ 时间戳值无效")
            return False
    except ValueError:
        print("❌ 时间戳格式错误")
        return False

def test_single_file_upload():
    """测试单个文件上传"""
    print("\n📤 测试单个文件上传...")
    
    s3_uploader = S3Uploader()
    if not s3_uploader.is_configured():
        print("⚠️ S3未配置，跳过上传测试")
        return False
    
    # 创建测试文件
    temp_dir, zip_file, md_file, html_file = create_test_files()
    
    try:
        # 测试上传ZIP文件
        folder_name = s3_uploader.create_folder_with_timestamp()
        s3_key = f"{folder_name}/test_upload.zip"
        
        metadata = {
            'test-upload': 'true',
            'upload-time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'file-type': 'test-zip'
        }
        
        print(f"上传文件: {zip_file} -> s3://{s3_uploader.bucket_name}/{s3_key}")
        
        result = s3_uploader.upload_file(zip_file, s3_key, metadata)
        
        if result:
            print("✅ 单个文件上传成功")
            return True
        else:
            print("❌ 单个文件上传失败")
            return False
            
    except Exception as e:
        print(f"❌ 上传过程中发生错误: {e}")
        return False
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)

def test_diagnostic_package_upload():
    """测试完整诊断包上传"""
    print("\n📦 测试完整诊断包上传...")
    
    s3_uploader = S3Uploader()
    if not s3_uploader.is_configured():
        print("⚠️ S3未配置，跳过上传测试")
        return False
    
    # 创建测试文件
    temp_dir, zip_file, md_file, html_file = create_test_files()
    
    try:
        print(f"上传诊断包:")
        print(f"  ZIP: {zip_file}")
        print(f"  MD:  {md_file}")
        print(f"  HTML: {html_file}")
        
        result = s3_uploader.upload_diagnostic_package(
            zip_file, md_file, html_file, "test_diagnostic.zip"
        )
        
        print(f"上传结果: {result}")
        
        if result['success']:
            print("✅ 完整诊断包上传成功")
            print(f"📁 S3文件夹: {result['folder']}")
            print(f"🪣 S3桶: {result['bucket']}")
            return True
        else:
            print(f"❌ 完整诊断包上传失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 上传过程中发生错误: {e}")
        return False
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)

def test_presigned_url():
    """测试预签名URL生成"""
    print("\n🔗 测试预签名URL生成...")
    
    s3_uploader = S3Uploader()
    if not s3_uploader.is_configured():
        print("⚠️ S3未配置，跳过URL生成测试")
        return False
    
    # 使用一个假设存在的文件键
    test_key = "test_folder/test_file.txt"
    url = s3_uploader.get_file_url(test_key, expiration=300)  # 5分钟过期
    
    if url:
        print(f"✅ 预签名URL生成成功")
        print(f"🔗 URL: {url[:100]}..." if len(url) > 100 else f"🔗 URL: {url}")
        return True
    else:
        print("❌ 预签名URL生成失败")
        return False

def main():
    """主测试函数"""
    print("🧪 S3上传功能测试开始")
    print("=" * 50)
    
    tests = [
        ("配置测试", test_s3_configuration),
        ("连接测试", test_s3_connection),
        ("时间戳测试", test_timestamp_folder),
        ("单文件上传测试", test_single_file_upload),
        ("诊断包上传测试", test_diagnostic_package_upload),
        ("预签名URL测试", test_presigned_url),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name}失败")
        except Exception as e:
            print(f"❌ {test_name}异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"🧪 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")
        return 1

if __name__ == "__main__":
    sys.exit(main())