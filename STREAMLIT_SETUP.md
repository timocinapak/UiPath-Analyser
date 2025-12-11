# 🚀 Streamlit Web Application Setup

## Installation

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install streamlit>=1.28.0
pip install pandas>=1.5.0
pip install reportlab>=4.0.0
```

### 2. Verify Installation

```bash
streamlit --version
python -c "import streamlit; print('✅ Streamlit is installed!')"
```

## Running the Application

### Start the Streamlit App

```bash
# From the project directory
streamlit run app.py

# Or from any location with full path
streamlit run /path/to/app.py
```

The app will open in your browser at `http://localhost:8501`

### Advanced Options

```bash
# Run on specific port
streamlit run app.py --server.port 8502

# Run on specific address
streamlit run app.py --server.address 0.0.0.0

# Disable auto-rerun on file changes
streamlit run app.py --logger.level=debug

# Run in headless mode (no browser auto-open)
streamlit run app.py --server.headless true
```

## Features

### 📁 File Upload
- Upload XAML workflow files
- Upload project.json configuration files
- Automatic validation and parsing

### 📊 Real-time Analysis
- Instant workflow analysis
- Activity detection and classification
- Issue identification with severity levels
- Health score calculation

### 📋 Multiple Report Formats
- **Markdown**: Download as .md file
- **PDF**: Professional PDF report with formatting
- **JSON**: Structured data export for integration

### 💾 Export Options
- Download reports in multiple formats
- Preview reports before downloading
- Flexible export settings

## Architecture

```
Streamlit Frontend
        ↓
    (File Upload)
        ↓
Workflow Analyzer Module
        ↓
    (Analysis Engine)
        ↓
Report Generators
        ↓
(Markdown/PDF/JSON)
        ↓
Download/Display
```

## Usage Workflow

1. **Upload Files**
   - Drag & drop or click to upload XAML file
   - Upload corresponding project.json file

2. **Select Settings**
   - Choose export formats (Markdown, PDF, JSON)
   - View health score ranges

3. **Review Analysis**
   - Check overview with health score
   - Review activities breakdown
   - Examine identified issues
   - Read recommendations

4. **Export Results**
   - Download in preferred format
   - Preview reports in-app
   - Share with team members

## UI Components

### Tabs
- **Overview**: Summary metrics and purpose
- **Activities**: Workflow activity breakdown
- **Issues**: Detailed issue analysis by severity
- **Recommendations**: Improvement suggestions
- **Export**: Download reports

### Sidebar
- File upload controls
- Export format selection
- Settings and configuration
- Health score reference

### Metrics
- Real-time health score display
- Activity statistics
- Issue counts by severity
- Variable information

## Customization

### Change Port
Edit `streamlit run app.py --server.port 8502`

### Modify Styling
Update CSS in the `st.markdown()` section at the beginning of `main()`

### Add New Metrics
Extend the metrics display in Tab1 (Overview)

### Extend Report Formats
Add new generators to report generation functions

## Troubleshooting

### App Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify streamlit installation
pip list | grep streamlit

# Reinstall streamlit
pip uninstall streamlit && pip install streamlit
```

### File Upload Issues
- Ensure files are named correctly (Main.xaml, project.json)
- Check file sizes (should be < 50MB)
- Verify XAML is valid XML format
- Verify JSON is valid JSON format

### PDF Export Not Working
```bash
# Install reportlab
pip install reportlab

# Or upgrade it
pip install --upgrade reportlab
```

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill the process using port 8501
lsof -ti:8501 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8501    # Windows (to find PID)
taskkill /PID <PID> /F         # Windows (to kill)
```

## Performance Tips

### For Large Workflows
- Streamlit caches analysis results automatically
- Reloading the page will preserve previous analysis
- Use `st.cache_resource` decorator for heavy operations

### Memory Usage
- Temporary files are cleaned up automatically
- Analysis results are held in memory only during session

## Security

### File Handling
- Files are uploaded to temporary directory
- Deleted automatically after analysis
- No files are stored permanently

### Data Privacy
- All processing happens locally
- No data is sent to external services
- Analysis is performed on client machine

## Deployment

### Local Network
```bash
streamlit run app.py --server.address 0.0.0.0
```

Access from other machines: `http://<your-ip>:8501`

### Docker (Optional)
Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t uipath-analyzer .
docker run -p 8501:8501 uipath-analyzer
```

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 1.5.0+
- ReportLab 4.0.0+ (for PDF export)
- ~500MB disk space for dependencies

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Streamlit documentation: https://docs.streamlit.io
3. Check ReportLab documentation: https://www.reportlab.com/docs/reportlab-userguide.pdf

## Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the app
streamlit run app.py

# 3. Open browser to localhost:8501

# 4. Upload XAML and JSON files

# 5. Review analysis and export reports
```

---

**Last Updated**: December 11, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
