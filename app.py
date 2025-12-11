"""
UiPath Workflow Analyzer - Streamlit Web Application

Interactive web interface for analyzing UiPath workflows with file upload,
real-time analysis, and PDF export capabilities.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import os
from datetime import datetime
from io import BytesIO
import json

# Import analyzer modules
from workflow_analyzer_module import (
    analyze_workflow,
    XAMLParser,
    JSONConfigParser,
    WorkflowAnalyzer
)

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


# Configure Streamlit page
st.set_page_config(
    page_title="UiPath Workflow Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .issue-critical {
        background-color: #ffcccc;
        border-left: 4px solid #ff0000;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .issue-high {
        background-color: #ffe6cc;
        border-left: 4px solid #ff6600;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .issue-medium {
        background-color: #fff9cc;
        border-left: 4px solid #ffcc00;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .issue-low {
        background-color: #ccffcc;
        border-left: 4px solid #00cc00;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)


def get_health_color(score: float) -> str:
    """Get color based on health score"""
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    else:
        return "🔴"


def generate_pdf_report(analysis) -> BytesIO:
    """Generate PDF report using ReportLab"""
    if not HAS_REPORTLAB:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#ff7f0e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph("📋 UiPath Workflow Analysis Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary Section
    elements.append(Paragraph("Summary", heading_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Workflow Name', analysis.workflow_name],
        ['Health Score', f"{analysis.overall_health_score:.1f}/100"],
        ['Total Activities', str(len(analysis.activities))],
        ['Total Variables', str(len(analysis.variables))],
        ['Issues Found', str(len(analysis.issues))],
        ['Recommendations', str(len(analysis.recommendations))]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Issues Section
    if analysis.issues:
        elements.append(Paragraph("Issues Found", heading_style))
        
        for issue in analysis.issues:
            issue_text = f"""
            <b>Title:</b> {issue.title}<br/>
            <b>Severity:</b> {issue.severity}<br/>
            <b>Category:</b> {issue.category}<br/>
            <b>Description:</b> {issue.description}<br/>
            <b>Solution:</b> {issue.solution}
            """
            elements.append(Paragraph(issue_text, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
    
    # Recommendations Section
    if analysis.recommendations:
        elements.append(Paragraph("Recommendations", heading_style))
        
        for i, rec in enumerate(analysis.recommendations, 1):
            elements.append(Paragraph(f"{i}. {rec}", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def main():
    # Header
    st.markdown("""
    # 🤖 UiPath Workflow Analyzer
    ## Interactive Analysis & Reporting Tool
    """)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📁 Upload File")
        st.markdown("Upload your UiPath workflow file for analysis")
        
        xaml_file = st.file_uploader(
            "Upload XAML file (e.g., Main.xaml)",
            type=['xaml'],
            help="Select your UiPath workflow .xaml file"
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        export_format = st.multiselect(
            "Export Format",
            ["Markdown", "PDF", "JSON"],
            default=["Markdown"],
            help="Select formats for exporting analysis results"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Health Score Ranges")
        st.info("🟢 80-100: Excellent\n\n🟡 60-79: Good\n\n🔴 0-59: Needs Improvement")
    
    # Main content
    if xaml_file:
        # Save uploaded file to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            xaml_path = Path(temp_dir) / xaml_file.name
            
            # Write uploaded file
            xaml_path.write_bytes(xaml_file.getbuffer())
            
            # Run analysis
            with st.spinner("🔍 Analyzing workflow..."):
                try:
                    analysis = analyze_workflow(str(xaml_path))
                    
                    # Display tabs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📊 Overview",
                        "🔧 Activities",
                        "⚠️ Issues",
                        "💡 Recommendations",
                        "📥 Export"
                    ])
                    
                    # Tab 1: Overview
                    with tab1:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "Health Score",
                                f"{analysis.overall_health_score:.1f}/100",
                                delta=f"{get_health_color(analysis.overall_health_score)}",
                                delta_color="off"
                            )
                        
                        with col2:
                            st.metric("Total Activities", len(analysis.activities))
                        
                        with col3:
                            st.metric("Issues Found", len(analysis.issues))
                        
                        st.markdown("---")
                        
                        # Workflow Purpose
                        st.subheader("🎯 Workflow Purpose")
                        st.info(analysis.workflow_purpose)
                        
                        st.markdown("---")

                        st.subheader("🤖 İş Akışı Özeti")
                        st.write(analysis.prose_summary)
                        
                        st.markdown("---")
                        
                        # Variables Summary
                        st.subheader("🔤 Variables")
                        if analysis.variables:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Total Variables**: {len(analysis.variables)}")
                            with col2:
                                with st.expander("View All Variables"):
                                    for var in analysis.variables:
                                        st.code(var)
                        else:
                            st.warning("No variables found")

                        st.markdown("---")

                        # Components section
                        st.subheader("🧩 Components Used")
                        if analysis.components:
                            st.write(f"**Total Unique Components**: {len(analysis.components)}")
                            with st.expander("View All Components"):
                                for comp in analysis.components:
                                    st.code(comp)
                        else:
                            st.warning("No components (activity types) found.")

                        st.markdown("---")

                        # URLs section
                        st.subheader("🔗 URLs Found")
                        if analysis.urls:
                            st.write(f"**Total URLs Found**: {len(analysis.urls)}")
                            with st.expander("View All URLs"):
                                for url in analysis.urls:
                                    st.info(f"[{url}]({url})")
                        else:
                            st.warning("No URLs found in the workflow.")
                        
                        st.markdown("---")
                        
                        # Dependencies
                        if analysis.dependencies:
                            st.subheader("📦 Dependencies")
                            dep_data = {
                                "Package": list(analysis.dependencies.keys()),
                                "Version": list(analysis.dependencies.values())
                            }
                            st.table(dep_data)
                    
                    # Tab 2: Activities
                    with tab2:
                        st.subheader("📌 Workflow Activities")
                        
                        if analysis.activities:
                            # Group by type
                            from collections import Counter
                            activity_types = Counter(act.type for act in analysis.activities)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Activities", len(analysis.activities))
                            with col2:
                                st.metric("Activity Types", len(activity_types))
                            
                            st.markdown("---")
                            
                            # Activity breakdown
                            for act_type, count in activity_types.most_common():
                                with st.expander(f"**{act_type}** ({count})"):
                                    activities_of_type = [a for a in analysis.activities if a.type == act_type]
                                    for act in activities_of_type:
                                        st.write(f"**{act.name}**")
                                        st.caption(act.purpose)
                        else:
                            st.warning("No activities found")
                    
                    # Tab 3: Issues
                    with tab3:
                        st.subheader("⚠️ Issues & Problems")
                        
                        if analysis.issues:
                            # Summary by severity
                            from collections import Counter
                            severity_counts = Counter(issue.severity for issue in analysis.issues)
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("🔴 Critical", severity_counts.get("Critical", 0))
                            with col2:
                                st.metric("🟠 High", severity_counts.get("High", 0))
                            with col3:
                                st.metric("🟡 Medium", severity_counts.get("Medium", 0))
                            with col4:
                                st.metric("🟢 Low", severity_counts.get("Low", 0))
                            
                            st.markdown("---")
                            
                            # Filter by severity
                            severity_filter = st.selectbox(
                                "Filter by Severity",
                                ["All", "Critical", "High", "Medium", "Low"]
                            )
                            
                            st.markdown("---")
                            
                            # Display issues
                            filtered_issues = analysis.issues
                            if severity_filter != "All":
                                filtered_issues = [i for i in analysis.issues if i.severity == severity_filter]
                            
                            for issue in filtered_issues:
                                severity_colors = {
                                    "Critical": "issue-critical",
                                    "High": "issue-high",
                                    "Medium": "issue-medium",
                                    "Low": "issue-low"
                                }
                                
                                severity_emojis = {
                                    "Critical": "🔴",
                                    "High": "🟠",
                                    "Medium": "🟡",
                                    "Low": "🟢"
                                }
                                
                                st.markdown(f"""
                                <div class="{severity_colors[issue.severity]}">
                                    <h4>{severity_emojis[issue.severity]} {issue.title}</h4>
                                    <p><b>Category:</b> {issue.category}</p>
                                    <p><b>Location:</b> {issue.location}</p>
                                    <p><b>Problem:</b> {issue.description}</p>
                                    <p><b>Solution:</b> {issue.solution}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.success("✅ No issues found! Your workflow looks good!")
                    
                    # Tab 4: Recommendations
                    with tab4:
                        st.subheader("💡 Improvement Recommendations")
                        
                        if analysis.recommendations:
                            for i, rec in enumerate(analysis.recommendations, 1):
                                st.info(f"**{i}. {rec}**")
                        else:
                            st.success("✅ No recommendations at this time!")
                    
                    # Tab 5: Export
                    with tab5:
                        st.subheader("📥 Export Analysis Results")
                        
                        # Markdown Export
                        if "Markdown" in export_format:
                            st.markdown("#### 📄 Markdown Report")
                            
                            markdown_report = generate_markdown_report(analysis)
                            
                            st.download_button(
                                label="⬇️ Download Markdown Report",
                                data=markdown_report,
                                file_name=f"workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                            
                            with st.expander("Preview Markdown"):
                                st.markdown(markdown_report)
                        
                        st.markdown("---")
                        
                        # PDF Export
                        if "PDF" in export_format:
                            st.markdown("#### 📕 PDF Report")
                            
                            if HAS_REPORTLAB:
                                pdf_buffer = generate_pdf_report(analysis)
                                
                                st.download_button(
                                    label="⬇️ Download PDF Report",
                                    data=pdf_buffer,
                                    file_name=f"workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            else:
                                st.warning("⚠️ PDF export requires reportlab. Install with: `pip install reportlab`")
                        
                        st.markdown("---")
                        
                        # JSON Export
                        if "JSON" in export_format:
                            st.markdown("#### 📋 JSON Export")
                            
                            json_report = generate_json_report(analysis)
                            
                            st.download_button(
                                label="⬇️ Download JSON Report",
                                data=json_report,
                                file_name=f"workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                            
                            with st.expander("Preview JSON"):
                                st.json(json.loads(json_report))
                
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.exception(e)
    
    else:
        # Welcome message
        st.info("""
        ### 👋 Welcome to UiPath Workflow Analyzer
        
        This tool helps you analyze UiPath workflows and identify:
        - **Issues** in workflow design
        - **Performance** bottlenecks
        - **Best practice** violations
        - **Security** concerns
        
        **To get started:**
        1. Upload your XAML workflow file
        2. Review the analysis results
        3. Export the report in your preferred format
        """)
        
        # Example files section
        with st.expander("📚 Need example files?"):
            st.markdown("""
            You can download an example file from the project repository:
            - `xaml_files/Main.xaml` - Example workflow
            
            Or create your own UiPath project and export the .xaml file.
            """)


def generate_markdown_report(analysis) -> str:
    """Generate markdown report"""
    report = []
    
    report.append("# 📋 UiPath Workflow Analysis Report\n")
    report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n\n")
    
    # Summary
    report.append("## 📊 Summary\n\n")
    report.append(f"| Metric | Value |\n")
    report.append(f"|--------|-------|\n")
    report.append(f"| **Workflow Name** | {analysis.workflow_name} |\n")
    report.append(f"| **Health Score** | {analysis.overall_health_score:.1f}/100 |\n")
    report.append(f"| **Total Activities** | {len(analysis.activities)} |\n")
    report.append(f"| **Total Variables** | {len(analysis.variables)} |\n")
    report.append(f"| **Issues Found** | {len(analysis.issues)} |\n")
    report.append(f"| **Recommendations** | {len(analysis.recommendations)} |\n\n")
    
    # Purpose
    report.append("## 🎯 Workflow Purpose\n\n")
    report.append(f"{analysis.workflow_purpose}\n\n")
    
    # Activities
    report.append("## 📌 Activities\n\n")
    if analysis.activities:
        from collections import Counter
        activity_types = Counter(act.type for act in analysis.activities)
        for act_type, count in activity_types.most_common():
            report.append(f"### {act_type} ({count})\n")
            activities_of_type = [a for a in analysis.activities if a.type == act_type]
            for act in activities_of_type:
                report.append(f"- **{act.name}**: {act.purpose}\n")
            report.append("\n")
    
    # Variables
    report.append("## 🔤 Variables\n\n")
    if analysis.variables:
        for var in analysis.variables:
            report.append(f"- `{var}`\n")
    report.append("\n")
    
    # Issues
    report.append("## ⚠️ Issues\n\n")
    if analysis.issues:
        from collections import defaultdict
        by_severity = defaultdict(list)
        for issue in analysis.issues:
            by_severity[issue.severity].append(issue)
        
        for severity in ["Critical", "High", "Medium", "Low"]:
            if severity in by_severity:
                report.append(f"### {severity}\n\n")
                for issue in by_severity[severity]:
                    report.append(f"**{issue.title}**\n")
                    report.append(f"- **Category**: {issue.category}\n")
                    report.append(f"- **Location**: {issue.location}\n")
                    report.append(f"- **Problem**: {issue.description}\n")
                    report.append(f"- **Solution**: {issue.solution}\n\n")
    else:
        report.append("✅ No issues found!\n\n")
    
    # Recommendations
    report.append("## 💡 Recommendations\n\n")
    if analysis.recommendations:
        for i, rec in enumerate(analysis.recommendations, 1):
            report.append(f"{i}. {rec}\n")
    report.append("\n")
    
    # Dependencies
    if analysis.dependencies:
        report.append("## 📦 Dependencies\n\n")
        for dep, version in analysis.dependencies.items():
            report.append(f"- `{dep}`: {version}\n")
    
    return "\n".join(report)


def generate_json_report(analysis) -> str:
    """Generate JSON report"""
    report_dict = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "tool": "UiPath Workflow Analyzer",
            "version": "1.0.0"
        },
        "summary": {
            "workflow_name": analysis.workflow_name,
            "health_score": round(analysis.overall_health_score, 2),
            "activities_count": len(analysis.activities),
            "variables_count": len(analysis.variables),
            "issues_count": len(analysis.issues),
            "recommendations_count": len(analysis.recommendations)
        },
        "workflow_purpose": analysis.workflow_purpose,
        "activities": [
            {
                "name": act.name,
                "type": act.type,
                "purpose": act.purpose
            }
            for act in analysis.activities
        ],
        "variables": analysis.variables,
        "issues": [
            {
                "title": issue.title,
                "severity": issue.severity,
                "category": issue.category,
                "description": issue.description,
                "location": issue.location,
                "solution": issue.solution
            }
            for issue in analysis.issues
        ],
        "recommendations": analysis.recommendations,
        "dependencies": analysis.dependencies
    }
    
    return json.dumps(report_dict, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
