import os
from pathlib import Path

def load_env_file(env_file_path='.env'):
    """
    加载.env文件中的环境变量
    
    Args:
        env_file_path: .env文件路径，默认为当前目录下的.env文件
    """
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / env_file_path
    
    if not env_path.exists():
        print(f"⚠️  .env文件不存在: {env_path}")
        return
    
    print(f"📄 加载.env文件: {env_path}")
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号（如果有）
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # 设置环境变量（如果尚未设置）
                    if key not in os.environ:
                        os.environ[key] = value
                        print(f"✅ 设置环境变量: {key}")
                    else:
                        print(f"⚠️  环境变量已存在，跳过: {key}")
                else:
                    print(f"⚠️  第{line_num}行格式错误: {line}")
    
    except Exception as e:
        print(f"❌ 加载.env文件失败: {e}")

if __name__ == "__main__":
    load_env_file() 