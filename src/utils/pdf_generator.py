"""
PDF Report Generator for Learning Sessions
Generates comprehensive PDF reports with session details, analytics, and recommendations.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
import os

class LearningReportGenerator:
    """Generate PDF reports for learning sessions."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            spaceAfter=10
        ))
    
    def generate_report(self, session_data):
        """
        Generate comprehensive PDF report.
        
        Args:
            session_data (dict): Complete session information
                - checkpoints: List of completed checkpoints
                - overall_score: Average score
                - total_time: Total time spent
                - completion_date: Session completion datetime
                - user_notes: Initial user notes
                
        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build document content
        story = []
        
        # Title Page
        story.extend(self._build_title_page(session_data))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._build_summary(session_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Checkpoint Details
        story.extend(self._build_checkpoint_details(session_data))
        story.append(PageBreak())
        
        # Performance Analytics
        story.extend(self._build_analytics(session_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Feynman Explanations (if any)
        if session_data.get('feynman_used', False):
            story.extend(self._build_feynman_section(session_data))
            story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        story.extend(self._build_recommendations(session_data))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _build_title_page(self, session_data):
        """Build title page."""
        elements = []
        
        # Title
        title = Paragraph(
            "🎓 Learning Session Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # Session info table
        completion_date = session_data.get('completion_date', datetime.now())
        date_str = completion_date.strftime("%B %d, %Y at %I:%M %p")
        
        info_data = [
            ['Session Date:', date_str],
            ['Total Checkpoints:', str(len(session_data.get('checkpoints', [])))],
            ['Overall Score:', f"{session_data.get('overall_score', 0):.1%}"],
            ['Time Spent:', self._format_time(session_data.get('total_time', 0))],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONT', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Status badge
        overall_score = session_data.get('overall_score', 0)
        status_color = colors.green if overall_score >= 0.7 else colors.orange if overall_score >= 0.5 else colors.red
        status_text = "✅ EXCELLENT" if overall_score >= 0.7 else "⚠️ GOOD EFFORT" if overall_score >= 0.5 else "❌ NEEDS IMPROVEMENT"
        
        status = Paragraph(
            f'<para align="center" fontSize="18" textColor="{status_color.hexval()}"><b>{status_text}</b></para>',
            self.styles['CustomBody']
        )
        elements.append(status)
        
        return elements
    
    def _build_summary(self, session_data):
        """Build executive summary."""
        elements = []
        
        heading = Paragraph("📊 Executive Summary", self.styles['CustomHeading'])
        elements.append(heading)
        
        # Summary statistics
        checkpoints = session_data.get('checkpoints', [])
        passed_count = sum(1 for cp in checkpoints if cp.get('passed', False))
        feynman_count = sum(1 for cp in checkpoints if cp.get('feynman_used', False))
        
        summary_text = f"""
        This learning session covered <b>{len(checkpoints)} checkpoint(s)</b> with an overall 
        performance score of <b>{session_data.get('overall_score', 0):.1%}</b>.<br/><br/>
        
        <b>Key Metrics:</b><br/>
        • Checkpoints Passed: {passed_count}/{len(checkpoints)}<br/>
        • Feynman Teaching Used: {feynman_count} time(s)<br/>
        • Average Score: {session_data.get('overall_score', 0):.1%}<br/>
        • Total Questions: {sum(len(cp.get('questions', [])) for cp in checkpoints)}<br/>
        • Time Investment: {self._format_time(session_data.get('total_time', 0))}<br/>
        """
        
        summary = Paragraph(summary_text, self.styles['CustomBody'])
        elements.append(summary)
        
        return elements
    
    def _build_checkpoint_details(self, session_data):
        """Build detailed checkpoint information."""
        elements = []
        
        heading = Paragraph("📝 Checkpoint Details", self.styles['CustomHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.2*inch))
        
        checkpoints = session_data.get('checkpoints', [])
        
        for i, checkpoint in enumerate(checkpoints, 1):
            # Checkpoint header
            cp_title = f"Checkpoint {i}: {checkpoint.get('topic', 'Unknown')}"
            cp_score = checkpoint.get('score', 0)
            cp_passed = checkpoint.get('passed', False)
            
            status_icon = "✅" if cp_passed else "❌"
            cp_header = Paragraph(
                f'<b>{status_icon} {cp_title}</b> - Score: {cp_score:.1%}',
                self.styles['CustomHeading']
            )
            elements.append(cp_header)
            elements.append(Spacer(1, 0.1*inch))
            
            # Questions and answers
            questions = checkpoint.get('questions', [])
            answers = checkpoint.get('answers', [])
            
            for j, (question, answer) in enumerate(zip(questions, answers), 1):
                # Question
                q_text = f"<b>Question {j}:</b> {question.get('question', '')}"
                elements.append(Paragraph(q_text, self.styles['CustomBody']))
                
                # Answer
                a_text = f"<b>Your Answer:</b> {answer.get('answer', '')[:200]}..."
                elements.append(Paragraph(a_text, self.styles['CustomBody']))
                
                # Evaluation
                eval_text = f"<b>Objective:</b> {question.get('objective', '')}"
                elements.append(Paragraph(eval_text, self.styles['CustomBody']))
                elements.append(Spacer(1, 0.1*inch))
            
            # Feynman teaching if used
            if checkpoint.get('feynman_used', False):
                feynman_heading = Paragraph(
                    "💡 <b>Feynman Teaching Applied</b>",
                    self.styles['CustomBody']
                )
                elements.append(feynman_heading)
                
                for explanation in checkpoint.get('feynman_explanations', []):
                    concept = explanation.get('concept', '')
                    exp_text = explanation.get('explanation', '')
                    
                    exp_para = Paragraph(
                        f"<b>{concept}:</b> {exp_text[:300]}...",
                        self.styles['CustomBody']
                    )
                    elements.append(exp_para)
                    elements.append(Spacer(1, 0.1*inch))
            
            elements.append(Spacer(1, 0.2*inch))
            
            if i < len(checkpoints):
                elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _build_analytics(self, session_data):
        """Build performance analytics section."""
        elements = []
        
        heading = Paragraph("📈 Performance Analytics", self.styles['CustomHeading'])
        elements.append(heading)
        elements.append(Spacer(1, 0.1*inch))
        
        checkpoints = session_data.get('checkpoints', [])
        
        # Performance table
        table_data = [['Checkpoint', 'Topic', 'Score', 'Status', 'Feynman']]
        
        for i, cp in enumerate(checkpoints, 1):
            topic = cp.get('topic', 'N/A')[:30]
            score = f"{cp.get('score', 0):.1%}"
            status = '✅ Pass' if cp.get('passed', False) else '❌ Fail'
            feynman = '💡 Yes' if cp.get('feynman_used', False) else '-'
            
            table_data.append([f"#{i}", topic, score, status, feynman])
        
        perf_table = Table(table_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(perf_table)
        
        return elements
    
    def _build_feynman_section(self, session_data):
        """Build Feynman teaching section."""
        elements = []
        
        heading = Paragraph("🎓 Feynman Teaching Summary", self.styles['CustomHeading'])
        elements.append(heading)
        
        text = Paragraph(
            "The Feynman Technique was applied to help simplify complex concepts. "
            "Review these explanations to strengthen your understanding.",
            self.styles['CustomBody']
        )
        elements.append(text)
        
        return elements
    
    def _build_recommendations(self, session_data):
        """Build recommendations section."""
        elements = []
        
        heading = Paragraph("🎯 Recommendations", self.styles['CustomHeading'])
        elements.append(heading)
        
        checkpoints = session_data.get('checkpoints', [])
        overall_score = session_data.get('overall_score', 0)
        
        # Generate personalized recommendations
        weak_topics = [cp.get('topic', '') for cp in checkpoints if cp.get('score', 0) < 0.7]
        
        recommendations = []
        
        if overall_score >= 0.8:
            recommendations.append("🌟 Excellent performance! You've demonstrated strong mastery.")
            recommendations.append("💪 Challenge yourself with more advanced topics.")
        elif overall_score >= 0.7:
            recommendations.append("✅ Good job! You've passed all checkpoints.")
            recommendations.append("📚 Review the concepts where you scored below 80%.")
        else:
            recommendations.append("📖 Consider reviewing the material again.")
            recommendations.append("👨‍🏫 The Feynman explanations provided should help clarify concepts.")
        
        if weak_topics:
            recommendations.append(f"🎯 Focus areas: {', '.join(weak_topics[:3])}")
        
        recommendations.append("⏰ Take breaks between learning sessions for better retention.")
        recommendations.append("🔄 Practice regularly to reinforce your knowledge.")
        
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer = Paragraph(
            '<para align="center"><i>Generated by Autonomous Learning Agent - Keep Learning! 🚀</i></para>',
            self.styles['CustomBody']
        )
        elements.append(footer)
        
        return elements
    
    def _format_time(self, seconds):
        """Format time in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} min"
