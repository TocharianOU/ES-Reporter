# Elasticsearch Inspection Tool 🔍

[中文](README-zh.md) | **English**

A modern web application for analyzing Elasticsearch diagnostic files and generating comprehensive inspection reports.

## 🌐 Live Demo

> 🚀 **Try it now**: [http://esreport.tocharian.eu/esreport/](http://esreport.tocharian.eu/esreport/)  
> Upload your Elasticsearch diagnostic files and experience the complete inspection report generation workflow

## ✨ Features

- 🌐 **Web Interface**: Modern drag-and-drop upload interface
- 📁 **ZIP Support**: Automatic extraction and analysis of Elasticsearch diagnostic files  
- 🔄 **Real-time Progress**: Dynamic progress bars showing processing status
- 📊 **Smart Analysis**: Automatic analysis of cluster health, configuration, and performance
- 📄 **Multiple Formats**: Support for Markdown and HTML report downloads
- 🎨 **Beautiful Display**: Optimized HTML rendering with print and export support
- 💻 **Responsive Design**: Compatible with desktop and mobile devices

## 🚀 Quick Start

### Requirements

- Python 3.8+
- uv (Python package manager)

### Installation

```bash
# Clone the project
git clone https://github.com/TocharianOU/es-report-tool.git
cd ES-Reporter

# Install dependencies
uv sync
```

### Running the Application

```bash
# Start web service
uv run python app.py

# Or with debug mode
uv run python app.py --debug

# Custom port
uv run python app.py --port 8080
```

Access http://localhost:5000 to get started.

## 📁 Project Structure

```
ES-Reporter/
├── app.py                 # Main web application
├── src/
│   ├── report_generator.py   # Report generation core
│   ├── html_converter.py     # HTML converter
│   └── inspector.py          # ES data inspector
├── templates/
│   └── index.html           # Web interface template
├── test_html_conversion.py  # HTML conversion tests
├── test_report_generation.py # Report generation tests
├── test_md_to_html.py       # Markdown to HTML tests
└── pyproject.toml          # Project configuration
```

## 🔧 Usage

### Web Interface

1. **Upload Files**: Drag and drop or select ZIP format Elasticsearch diagnostic files
2. **Wait for Processing**: Watch the progress bar through upload, extraction, analysis, and report generation
3. **View Reports**: Preview the generated inspection report in the page
4. **Download Reports**: Choose Markdown or HTML format for download

### Command Line

```bash
# Generate report (specify data directory)
uv run python -m src.report_generator /path/to/diagnostic/data

# Test HTML conversion
uv run python test_html_conversion.py

# Test report generation
uv run python test_report_generation.py
```

## 📊 Report Contents

Inspection reports include the following sections:

- **📋 Report Overview**: Executive summary and key metrics
- **🎯 Executive Summary**: Overall health status and important findings  
- **⚙️ Cluster Basic Info**: Version, configuration, and node information
- **🖥️ Node Details**: Detailed status of each node
- **📚 Index Analysis**: Index health and performance metrics
- **💡 Final Recommendations**: Optimization suggestions and action plans
- **📝 Log Analysis**: Error and warning log summaries

## 🧪 Testing

```bash
# Run HTML conversion tests
uv run python test_html_conversion.py

# Run complete functionality tests
uv run python test_report_generation.py

# Run Markdown to HTML conversion tests
uv run python test_md_to_html.py
```

## 📋 Dependencies

Core dependencies:
- Flask: Web framework
- Jinja2: Template engine  
- Werkzeug: WSGI toolkit
- jsonpath-ng: JSON data querying
- Markdown: Markdown processing

Development dependencies:
- pytest: Testing framework

## 🎨 HTML Report Features

Generated HTML reports have the following characteristics:

- 📱 **Responsive Design**: Adapts to various screen sizes
- 🖨️ **Print Optimized**: Specialized print styles, can be directly printed or exported to PDF
- 📊 **Beautiful Tables**: Clear table displays with stripe and hover effects
- 🎯 **Navigation Friendly**: Clear heading hierarchy and content structure
- 💻 **Web Friendly**: Perfect display in browsers

## 🐳 Docker Deployment

```bash
# Build image
docker build -t es-report-tool .

# Run container
docker run -p 5000:5000 es-report-tool
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 📞 Support

For questions or suggestions, please create an Issue or contact the maintainers.

---

**Tip**: HTML reports can be directly printed to PDF in browsers, with better results than dedicated PDF generators! 🎯 
