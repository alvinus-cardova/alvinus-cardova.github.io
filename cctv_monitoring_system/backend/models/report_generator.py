import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import base64

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, reports_dir: str = "reports", charts_dir: str = "data/charts"):
        """
        Initialize report generator
        
        Args:
            reports_dir: Directory for PDF reports
            charts_dir: Directory for generated charts
        """
        self.reports_dir = Path(reports_dir)
        self.charts_dir = Path(charts_dir)
        
        # Create directories if they don't exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    async def generate_report(self, report_type: str = "daily", 
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> str:
        """
        Generate compliance report
        
        Args:
            report_type: Type of report (daily, weekly, monthly)
            start_date: Start date for report (ISO format)
            end_date: End date for report (ISO format)
            
        Returns:
            Path to generated PDF report
        """
        try:
            # Determine date range
            if start_date is None:
                if report_type == "daily":
                    start_date = datetime.now().strftime('%Y-%m-%d')
                    end_date = start_date
                elif report_type == "weekly":
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                elif report_type == "monthly":
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Generate report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ppe_compliance_report_{report_type}_{timestamp}.pdf"
            report_path = self.reports_dir / filename
            
            # Get violation data
            violations = await self._get_violations_for_period(start_date, end_date)
            
            # Generate charts
            charts = await self._generate_charts(violations, start_date, end_date)
            
            # Create PDF report
            await self._create_pdf_report(report_path, violations, charts, 
                                        report_type, start_date, end_date)
            
            logger.info(f"Report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    async def generate_daily_report(self) -> str:
        """
        Generate daily compliance report
        
        Returns:
            Path to generated PDF report
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return await self.generate_report("daily", today, today)
    
    async def _get_violations_for_period(self, start_date: str, end_date: str) -> list:
        """
        Get violations for the specified period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of violation records
        """
        try:
            violations = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Load violations from daily log files
            current_dt = start_dt
            while current_dt <= end_dt:
                date_str = current_dt.strftime('%Y-%m-%d')
                log_file = Path("logs") / f"violations_{date_str}.json"
                
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        daily_violations = json.load(f)
                        violations.extend(daily_violations)
                
                current_dt += timedelta(days=1)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error getting violations for period: {e}")
            return []
    
    async def _generate_charts(self, violations: list, start_date: str, end_date: str) -> Dict[str, str]:
        """
        Generate charts for the report
        
        Args:
            violations: List of violation records
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with chart file paths
        """
        try:
            charts = {}
            
            if not violations:
                return charts
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(violations)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            # 1. Violations by type chart
            violation_counts = df['type'].value_counts()
            plt.figure(figsize=(10, 6))
            violation_counts.plot(kind='bar', color='skyblue')
            plt.title('Violations by Type', fontsize=14, fontweight='bold')
            plt.xlabel('Violation Type')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = self.charts_dir / f"violations_by_type_{start_date}_{end_date}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts['violations_by_type'] = str(chart_path)
            
            # 2. Violations over time chart
            daily_counts = df.groupby('date').size()
            plt.figure(figsize=(12, 6))
            daily_counts.plot(kind='line', marker='o', linewidth=2, markersize=6)
            plt.title('Violations Over Time', fontsize=14, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Number of Violations')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            chart_path = self.charts_dir / f"violations_over_time_{start_date}_{end_date}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts['violations_over_time'] = str(chart_path)
            
            # 3. Confidence distribution chart
            plt.figure(figsize=(10, 6))
            plt.hist(df['confidence'], bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
            plt.title('Detection Confidence Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Confidence Score')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            chart_path = self.charts_dir / f"confidence_distribution_{start_date}_{end_date}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts['confidence_distribution'] = str(chart_path)
            
            # 4. Heatmap of violations by hour and type
            df['hour'] = df['timestamp'].dt.hour
            pivot_table = df.pivot_table(index='hour', columns='type', values='confidence', aggfunc='count', fill_value=0)
            
            plt.figure(figsize=(12, 8))
            sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Violation Count'})
            plt.title('Violations by Hour and Type', fontsize=14, fontweight='bold')
            plt.xlabel('Violation Type')
            plt.ylabel('Hour of Day')
            plt.tight_layout()
            
            chart_path = self.charts_dir / f"violations_heatmap_{start_date}_{end_date}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts['violations_heatmap'] = str(chart_path)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            return {}
    
    async def _create_pdf_report(self, report_path: Path, violations: list, 
                                charts: Dict[str, str], report_type: str,
                                start_date: str, end_date: str):
        """
        Create PDF report
        
        Args:
            report_path: Path to save PDF report
            violations: List of violation records
            charts: Dictionary with chart file paths
            report_type: Type of report
            start_date: Start date
            end_date: End date
        """
        try:
            doc = SimpleDocTemplate(str(report_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            story.append(Paragraph("PPE Compliance Report", title_style))
            story.append(Spacer(1, 20))
            
            # Report metadata
            meta_style = ParagraphStyle(
                'MetaData',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20
            )
            
            story.append(Paragraph(f"<b>Report Type:</b> {report_type.title()}", meta_style))
            story.append(Paragraph(f"<b>Period:</b> {start_date} to {end_date}", meta_style))
            story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
            story.append(Paragraph(f"<b>Total Violations:</b> {len(violations)}", meta_style))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            if violations:
                # Calculate statistics
                total_violations = len(violations)
                violation_types = {}
                for v in violations:
                    v_type = v['type']
                    violation_types[v_type] = violation_types.get(v_type, 0) + 1
                
                avg_confidence = sum(v['confidence'] for v in violations) / len(violations)
                
                summary_text = f"""
                During the reporting period, {total_violations} PPE violations were detected across the monitored areas.
                
                Key findings:
                • Most common violation: {max(violation_types, key=violation_types.get) if violation_types else 'N/A'}
                • Average detection confidence: {avg_confidence:.1%}
                • Violation types detected: {len(violation_types)}
                
                The system successfully identified safety compliance issues and provided real-time alerts to ensure immediate response to potential hazards.
                """
            else:
                summary_text = "No violations were detected during the reporting period. All monitored personnel were compliant with PPE requirements."
            
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Violations by Type
            if violations:
                story.append(Paragraph("Violations by Type", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Create table
                violation_types = {}
                for v in violations:
                    v_type = v['type']
                    violation_types[v_type] = violation_types.get(v_type, 0) + 1
                
                table_data = [['Violation Type', 'Count', 'Percentage']]
                total = len(violations)
                for v_type, count in sorted(violation_types.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total) * 100
                    table_data.append([v_type, str(count), f"{percentage:.1f}%"])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 20))
            
            # Charts
            if charts:
                story.append(Paragraph("Visual Analysis", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                for chart_name, chart_path in charts.items():
                    if Path(chart_path).exists():
                        # Add chart title
                        chart_title = chart_name.replace('_', ' ').title()
                        story.append(Paragraph(chart_title, styles['Heading3']))
                        story.append(Spacer(1, 6))
                        
                        # Add chart image
                        img = Image(chart_path, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
            
            # Recommendations
            story.append(Paragraph("Recommendations", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            recommendations = [
                "1. Conduct regular PPE training sessions for all personnel",
                "2. Implement stricter enforcement of safety protocols",
                "3. Install additional safety equipment in high-violation areas",
                "4. Review and update safety procedures based on violation patterns",
                "5. Schedule regular safety audits and inspections"
            ]
            
            for rec in recommendations:
                story.append(Paragraph(rec, styles['Normal']))
                story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            
        except Exception as e:
            logger.error(f"Error creating PDF report: {e}")
            raise
    
    def get_report_status(self) -> Dict[str, Any]:
        """
        Get report generator status
        
        Returns:
            Dictionary with report generator status
        """
        try:
            # Count report files
            report_files = list(self.reports_dir.glob("*.pdf"))
            chart_files = list(self.charts_dir.glob("*.png"))
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in report_files + chart_files)
            
            return {
                'reports_directory': str(self.reports_dir),
                'charts_directory': str(self.charts_dir),
                'report_files_count': len(report_files),
                'chart_files_count': len(chart_files),
                'total_size_mb': total_size / (1024 * 1024),
                'latest_report': max(report_files, key=lambda x: x.stat().st_mtime).name if report_files else None
            }
            
        except Exception as e:
            logger.error(f"Error getting report status: {e}")
            return {}