FROM python:3.11-slim AS base

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 设置工作目录
WORKDIR /app

# 先复制项目配置文件和 README
COPY pyproject.toml ./
COPY requirements.txt ./
COPY README.md ./

# 使用 uv 安装依赖
RUN uv pip install --system -e .

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 设置启动用户 (安全性)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 启动命令
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "5000"] 