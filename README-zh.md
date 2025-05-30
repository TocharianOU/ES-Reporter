# Elasticsearch 巡检工具 🔍

**中文** | [English](README.md)

一个现代化的Web应用，用于分析Elasticsearch诊断文件并生成详细的巡检报告。

## 🌐 在线体验

> 🚀 **立即试用**: [http://esreport.tocharian.eu/esreport/](http://esreport.tocharian.eu/esreport/)  
> 上传您的Elasticsearch诊断文件，体验完整的巡检报告生成流程

## ✨ 功能特性

- 🌐 **Web界面**: 现代化的拖拽上传界面
- 📁 **ZIP文件支持**: 自动解压和分析Elasticsearch诊断文件  
- 🔄 **实时进度**: 动态进度条显示处理状态
- 📊 **智能分析**: 自动分析集群健康状态、配置和性能
- 📄 **多格式报告**: 支持Markdown和HTML格式下载
- 🎨 **美观展示**: 优化的HTML显示效果，支持打印和导出
- 💻 **响应式设计**: 适配桌面和移动设备

## 🚀 快速开始

### 环境要求

- Python 3.8+
- uv (Python包管理器)

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/TocharianOU/es-report-tool.git
cd es_report_tool

# 安装依赖
uv sync
```

### 运行应用

```bash
# 启动Web服务
uv run python app.py

# 或使用调试模式
uv run python app.py --debug

# 自定义端口
uv run python app.py --port 8080
```

访问 http://localhost:5000 开始使用。

## 📁 项目结构

```
es_report_tool/
├── app.py                 # Web应用主文件
├── src/
│   ├── report_generator.py   # 报告生成核心
│   ├── html_converter.py     # HTML转换器
│   └── inspector.py          # ES数据检查器
├── templates/
│   └── index.html           # Web界面模板
├── test_html_conversion.py  # HTML转换测试
├── test_report_generation.py # 报告生成测试
├── test_md_to_html.py       # Markdown转HTML测试
└── pyproject.toml          # 项目配置
```

## 🔧 使用方法

### Web界面使用

1. **上传文件**: 拖拽或选择ZIP格式的Elasticsearch诊断文件
2. **等待处理**: 观察进度条，包含上传、解压、分析、生成报告等步骤
3. **查看报告**: 在页面中预览生成的巡检报告
4. **下载报告**: 选择Markdown或HTML格式下载

### 命令行使用

```bash
# 生成报告（指定数据目录）
uv run python -m src.report_generator /path/to/diagnostic/data

# 测试HTML转换
uv run python test_html_conversion.py

# 测试报告生成
uv run python test_report_generation.py
```

## 📊 报告内容

巡检报告包含以下部分：

- **📋 报告概览**: 执行摘要和关键指标
- **🎯 执行摘要**: 总体健康状况和重要发现  
- **⚙️ 集群基础信息**: 版本、配置、节点信息
- **🖥️ 节点详情**: 每个节点的详细状态
- **📚 索引分析**: 索引健康状况和性能指标
- **💡 最终建议**: 优化建议和行动计划
- **📝 日志分析**: 错误和警告日志摘要

## 🧪 测试

```bash
# 运行HTML转换测试
uv run python test_html_conversion.py

# 运行完整功能测试
uv run python test_report_generation.py

# 运行Markdown到HTML转换测试
uv run python test_md_to_html.py
```

## 📋 依赖

核心依赖：
- Flask: Web框架
- Jinja2: 模板引擎  
- Werkzeug: WSGI工具库
- jsonpath-ng: JSON数据查询
- Markdown: Markdown处理

开发依赖：
- pytest: 测试框架

## 🎨 HTML报告特性

生成的HTML报告具有以下特性：

- 📱 **响应式设计**: 适配各种屏幕尺寸
- 🖨️ **打印优化**: 专门的打印样式，可直接打印或导出PDF
- 📊 **表格美化**: 清晰的表格显示，支持条纹和悬停效果
- 🎯 **导航友好**: 清晰的标题层级和内容结构
- 💻 **Web友好**: 在浏览器中完美显示

## 🐳 Docker部署

```bash
# 构建镜像
docker build -t es-report-tool .

# 运行容器
docker run -p 5000:5000 es-report-tool

# 后台运行容器
docker run -d -p 5000:5000 --name es-report-server es-report-tool
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 支持

如有问题或建议，请创建Issue或联系维护者。

---

**提示**: HTML报告可以在浏览器中直接打印为PDF，效果优于专用PDF生成器！🎯
