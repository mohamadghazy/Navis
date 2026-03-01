import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from config import CURRENCY

def export_to_excel(debts_df, expenses_df, income_df, settings):
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not debts_df.empty:
            debts_df.to_excel(writer, sheet_name='Debts', index=False)
        
        if not expenses_df.empty:
            expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
        
        if not income_df.empty:
            income_df.to_excel(writer, sheet_name='Income', index=False)
        
        summary_df = pd.DataFrame([{
            "Emergency Fund Target": settings.get("emergency_fund_target", 90000),
            "Currency": settings.get("currency", CURRENCY),
            "Created Date": settings.get("created_date", "")
        }])
        summary_df.to_excel(writer, sheet_name='Settings', index=False)
    
    output.seek(0)
    return output

def generate_pdf_report(username, debts_df, expenses_df, income_df, settings, summary_data):
    output = BytesIO()
    
    doc = SimpleDocTemplate(output, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    
    elements = []
    
    elements.append(Paragraph("Personal Finance Report", title_style))
    elements.append(Paragraph(f"Profile: {username}", styles['Normal']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Summary", heading_style))
    
    summary_table_data = [
        ["Metric", "Value"],
        ["Total Debt", f"{CURRENCY} {summary_data.get('total_debt', 0):,.0f}"],
        ["Monthly Expenses", f"{CURRENCY} {summary_data.get('monthly_expenses', 0):,.0f}"],
        ["Monthly Income", f"{CURRENCY} {summary_data.get('monthly_income', 0):,.0f}"],
        ["Monthly Surplus", f"{CURRENCY} {summary_data.get('monthly_surplus', 0):,.0f}"],
        ["Emergency Fund Target", f"{CURRENCY} {settings.get('emergency_fund_target', 90000):,.0f}"],
    ]
    
    summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    if not debts_df.empty:
        elements.append(Paragraph("Debts", heading_style))
        
        debt_data = [["Name", "Lender", "Balance", "Monthly Payment", "Status"]]
        for _, row in debts_df.iterrows():
            debt_data.append([
                str(row.get('name', '')),
                str(row.get('lender', '')),
                f"{CURRENCY} {row.get('balance', 0):,.0f}",
                f"{CURRENCY} {row.get('monthly_payment', 0):,.0f}",
                str(row.get('status', ''))
            ])
        
        debt_table = Table(debt_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1.2*inch, 0.8*inch])
        debt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(debt_table)
        elements.append(Spacer(1, 30))
    
    if not expenses_df.empty:
        elements.append(Paragraph("Monthly Expenses", heading_style))
        
        expense_data = [["Category", "Amount", "Frequency"]]
        for _, row in expenses_df.iterrows():
            expense_data.append([
                str(row.get('category', '')),
                f"{CURRENCY} {row.get('amount', 0):,.0f}",
                str(row.get('frequency', ''))
            ])
        
        expense_table = Table(expense_data, colWidths=[2*inch, 2*inch, 1.5*inch])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(expense_table)
        elements.append(Spacer(1, 30))
    
    if not income_df.empty:
        elements.append(Paragraph("Income Sources", heading_style))
        
        income_data = [["Source", "Amount", "Frequency", "Active"]]
        for _, row in income_df.iterrows():
            income_data.append([
                str(row.get('source', '')),
                f"{CURRENCY} {row.get('amount', 0):,.0f}",
                str(row.get('frequency', '')),
                "Yes" if row.get('is_active', True) else "No"
            ])
        
        income_table = Table(income_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 0.5*inch])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(income_table)
    
    doc.build(elements)
    output.seek(0)
    return output
