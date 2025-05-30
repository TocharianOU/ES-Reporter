# Elasticsearch 巡检工具 - 国际化功能文档

## 概述

本项目已成功实现完整的中英文双语支持，包括用户界面、报告内容、API响应等所有用户面向的文本内容。

## 支持的语言

- **中文 (zh)**: 简体中文，默认语言
- **英文 (en)**: 英语

## 国际化架构

### 1. 核心国际化模块 (`src/i18n.py`)

#### 主要功能
- 翻译字典管理
- 语言切换
- 浏览器语言自动检测
- 翻译文本获取

#### 使用方式
```python
from src.i18n import I18n, i18n

# 创建实例
i18n_instance = I18n('en')

# 获取翻译
title = i18n_instance.t('title', 'ui')

# 全局实例
i18n.set_language('en')
text = i18n.t('error_no_file', 'ui')
```

### 2. 报告生成国际化

#### 支持的模块
所有报告生成模块都支持语言参数：

1. **ReportOverviewGenerator** - 报告概述
2. **ExecutiveSummaryGenerator** - 执行摘要  
3. **ClusterBasicInfoGenerator** - 集群基础信息
4. **NodeInfoGenerator** - 节点信息
5. **IndexAnalysisGenerator** - 索引分析
6. **LogAnalysisGenerator** - 日志分析
7. **FinalRecommendationsGenerator** - 最终建议

#### 使用方式
```python
# 创建中文报告生成器
generator = ESReportGenerator(data_dir, output_dir, language='zh')

# 创建英文报告生成器
generator = ESReportGenerator(data_dir, output_dir, language='en')
```

### 3. Web API 国际化

#### 支持的接口

1. **`/api/translations`** - 获取翻译文本
   ```bash
   GET /api/translations?lang=en
   GET /api/translations?lang=zh
   ```

2. **`/api/set-language`** - 设置语言
   ```bash
   POST /api/set-language
   Content-Type: application/json
   
   {"language": "en"}
   ```

3. **`/api/upload-diagnostic`** - 上传文件（支持语言参数）
   ```bash
   POST /api/upload-diagnostic
   Content-Type: multipart/form-data
   
   diagnostic_file: [文件]
   language: en
   ```

## 翻译覆盖范围

### 1. 用户界面翻译 (ui)

包含所有前端界面文本：
- 页面标题和说明
- 按钮和操作文本
- 状态消息和进度提示
- 错误信息和警告
- 表单标签和帮助文本

### 2. 报告内容翻译 (report)

包含所有报告生成的文本：
- 章节标题和子标题
- 表格表头和描述
- 状态值和单位
- 分析描述和建议
- 技术术语和指标名称

## 语言检测和切换

### 1. 自动检测
- 系统会自动检测浏览器的 `Accept-Language` 头
- 支持中文 (`zh`, `cn`) 和英文 (`en`) 的识别
- 默认回退到中文

### 2. 手动切换
- 用户可通过界面语言选择器切换
- API支持动态语言设置
- 语言设置会影响后续的报告生成

## 模板系统

### 1. 动态模板
系统支持基于语言的动态模板生成：

**中文模板**:
```markdown
# Elasticsearch 集群巡检报告

## 1. 报告概述
{{REPORT_OVERVIEW}}

## 2. 执行摘要
{{EXECUTIVE_SUMMARY}}
...
```

**英文模板**:
```markdown
# Elasticsearch Cluster Inspection Report

## 1. Report Overview
{{REPORT_OVERVIEW}}

## 2. Executive Summary
{{EXECUTIVE_SUMMARY}}
...
```

### 2. 文件模板支持
- 支持 `templates/report_template.md` (中文)
- 支持 `templates/report_template_en.md` (英文)
- 自动回退到动态模板

## 实现细节

### 1. 模块级别国际化

每个报告生成模块都实现了语言支持：

```python
class ModuleGenerator:
    def __init__(self, data_loader: ESDataLoader, language: str = "zh"):
        self.language = language
        self.i18n = I18n(language)
    
    def generate(self) -> str:
        if self.language == 'en':
            content = "### English Content"
        else:
            content = "### 中文内容"
        return content
```

### 2. 条件式内容生成

根据语言参数生成不同的内容：

```python
if self.language == 'en':
    content += """### 5.1 Index Overview Statistics

| Metric | Value | Description |
|--------|-------|-------------|
"""
else:
    content += """### 5.1 索引概览统计

| 指标项 | 数值 | 说明 |
|--------|------|------|
"""
```

### 3. 翻译键值管理

使用层次化的翻译键值结构：

```python
TRANSLATIONS = {
    'zh': {
        'ui': { 'title': 'Elasticsearch 巡检工具' },
        'report': { 'cluster_overview': '集群概览' }
    },
    'en': {
        'ui': { 'title': 'Elasticsearch Inspection Tool' },
        'report': { 'cluster_overview': 'Cluster Overview' }
    }
}
```

## 质量保证

### 1. 测试覆盖
- 基础国际化功能测试
- 模板生成测试
- Web API翻译测试
- 完整报告生成测试

### 2. 错误处理
- 缺失翻译时的回退机制
- 无效语言参数的处理
- 模板加载失败的处理

### 3. 性能考虑
- 翻译文本的内存缓存
- 按需加载语言包
- 最小化翻译开销

## 使用指南

### 1. 开发者使用

**添加新的翻译文本**:
1. 在 `src/i18n.py` 的 `TRANSLATIONS` 字典中添加键值
2. 同时添加中文和英文版本
3. 使用 `i18n.t(key, category)` 获取翻译

**创建新的国际化模块**:
1. 在构造函数中接收 `language` 参数
2. 创建 `I18n` 实例
3. 使用条件语句或翻译键值生成内容

### 2. 用户使用

**Web界面**:
1. 访问系统时自动检测语言
2. 使用语言选择器手动切换
3. 上传文件时选择报告语言

**API调用**:
1. 通过 `language` 参数指定语言
2. 调用 `/api/set-language` 设置语言
3. 获取 `/api/translations` 获取翻译

## 扩展支持

### 1. 添加新语言

要添加新语言支持（如法语 `fr`）：

1. 在 `SUPPORTED_LANGUAGES` 中添加语言代码
2. 在 `TRANSLATIONS` 中添加对应的翻译字典
3. 更新语言检测逻辑
4. 添加对应的模板文件

### 2. 扩展翻译内容

1. 在对应的翻译分类中添加新的键值对
2. 确保所有支持的语言都有对应翻译
3. 在代码中使用 `i18n.t()` 获取翻译

## 技术规范

### 1. 编码规范
- 所有文本文件使用 UTF-8 编码
- 翻译键使用小写字母和下划线
- 分类名称使用简短的英文标识符

### 2. 命名约定
- 语言代码使用 ISO 639-1 标准 (zh, en)
- 翻译键名反映实际用途
- 分类名称简洁明确 (ui, report)

### 3. 文档要求
- 新增翻译需要添加对应文档
- API变更需要更新接口文档
- 重要功能需要提供使用示例

## 测试验证

运行以下命令验证国际化功能：

```bash
# 启动Web服务
python app.py

# 测试API翻译
curl "http://localhost:5000/api/translations?lang=en"
curl "http://localhost:5000/api/translations?lang=zh"

# 测试语言切换
curl -X POST "http://localhost:5000/api/set-language" \
     -H "Content-Type: application/json" \
     -d '{"language": "en"}'
```

## 故障排除

### 1. 常见问题

**翻译文本不显示**:
- 检查翻译键是否正确
- 确认语言参数传递
- 查看是否有回退翻译

**报告内容未国际化**:
- 确认模块构造时传递了语言参数
- 检查条件语句的语言判断
- 验证模板文件是否存在

### 2. 调试方法

1. 启用调试模式查看详细日志
2. 检查浏览器控制台的错误信息
3. 使用API直接测试翻译功能
4. 验证文件编码和路径正确性

---

## 总结

本项目的国际化实现涵盖了从用户界面到报告内容的完整双语支持，提供了灵活的扩展机制和完善的错误处理。用户可以无缝地在中英文之间切换，享受完全本地化的使用体验。