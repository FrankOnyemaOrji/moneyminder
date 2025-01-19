import io
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


class ReportGenerator:
    def __init__(self, transactions, filters):
        self.transactions = transactions
        self.filters = filters
        self.summary = self._calculate_summary()
        self.account = transactions[0].account if transactions else None

        # Define colors
        self.COLOR_INCOME = colors.HexColor('#4CAF50')  # Green
        self.COLOR_EXPENSE = colors.HexColor('#F44336')  # Red
        self.COLOR_HEADER = colors.HexColor('#F8F9FA')  # Light gray
        self.COLOR_BORDER = colors.HexColor('#DEE2E6')  # Light border

    def _calculate_summary(self):
        """Calculate report summary"""
        total_income = sum(float(t.amount) for t in self.transactions if t.transaction_type == 'income')
        total_expenses = sum(float(t.amount) for t in self.transactions if t.transaction_type == 'expense')

        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': total_income - total_expenses,
            'transaction_count': len(self.transactions)
        }

    def generate_excel(self):
        """Generate Excel report with enhanced formatting"""
        output = io.BytesIO()

        # Create account summary data
        summary_data = {
            'Account Name': self.account.name,
            'Account Category': self.account.account_type.title(),
            'Currency': self.account.currency,
            'Total Income': f"{self.account.currency} {self.summary['total_income']:,.2f}",
            'Total Expenses': f"{self.account.currency} {self.summary['total_expenses']:,.2f}",
            'Net Balance': f"{self.account.currency} {self.summary['balance']:,.2f}"
        }

        # Create transaction data
        transaction_data = []
        for t in self.transactions:
            transaction_data.append({
                'Date': t.date.strftime('%Y-%m-%d'),
                'Category': t.category,
                'Tag': t.tag,
                'Description': t.description,
                'Amount': float(t.amount),  # Keep as number for conditional formatting
                'Type': t.transaction_type.capitalize()
            })

        # Create Excel writer
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#f8f9fa',
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': 11
            })

            income_format = workbook.add_format({
                'font_color': '#4CAF50',
                'bold': True,
                'num_format': f'"{self.account.currency}" #,##0.00'
            })

            expense_format = workbook.add_format({
                'font_color': '#F44336',
                'bold': True,
                'num_format': f'"{self.account.currency}" #,##0.00'
            })

            date_format = workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'align': 'center'
            })

            # Create Summary sheet
            summary_df = pd.DataFrame([summary_data])
            summary_df.to_excel(writer, sheet_name='Summary', index=False, startrow=1)
            summary_sheet = writer.sheets['Summary']

            # Add title to summary sheet with date range
            title = f'Account Report ({self.filters.start_date.strftime("%Y-%m-%d")} to {self.filters.end_date.strftime("%Y-%m-%d")})'
            summary_sheet.merge_range('A1:F1', title,
                                      workbook.add_format({
                                          'bold': True,
                                          'align': 'center',
                                          'font_size': 14,
                                          'border': 1
                                      }))

            # Format Summary sheet
            for col_num, value in enumerate(summary_df.columns.values):
                summary_sheet.write(1, col_num, value, header_format)
                summary_sheet.set_column(col_num, col_num, 20)

            # Create Transactions sheet
            trans_df = pd.DataFrame(transaction_data)
            trans_df.to_excel(writer, sheet_name='Transactions', index=False)
            trans_sheet = writer.sheets['Transactions']

            # Format Transactions sheet
            for col_num, value in enumerate(trans_df.columns.values):
                trans_sheet.write(0, col_num, value, header_format)

            # Set column widths
            trans_sheet.set_column('A:A', 12)  # Date
            trans_sheet.set_column('B:B', 15)  # Category
            trans_sheet.set_column('C:C', 15)  # Tag
            trans_sheet.set_column('D:D', 40)  # Description
            trans_sheet.set_column('E:E', 15)  # Amount
            trans_sheet.set_column('F:F', 10)  # Type

            # Apply conditional formatting to Amount column
            trans_sheet.conditional_format(1, 4, len(transaction_data), 4, {
                'type': 'formula',
                'criteria': '=$F2="Income"',
                'format': income_format
            })
            trans_sheet.conditional_format(1, 4, len(transaction_data), 4, {
                'type': 'formula',
                'criteria': '=$F2="Expense"',
                'format': expense_format
            })

            # Format date column
            trans_sheet.set_column('A:A', 12, date_format)

            # Add filters to columns
            trans_sheet.autofilter(0, 0, len(transaction_data), len(trans_df.columns) - 1)

            # Freeze the header row
            trans_sheet.freeze_panes(1, 0)

        output.seek(0)
        return output

    def generate_pdf(self):
        """Generate PDF report with enhanced formatting"""
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements = []

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2C3E50'),
            alignment=1  # Center alignment
        )

        subtitle_style = ParagraphStyle(
            'CustomSubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceBefore=20,
            spaceAfter=20,
            alignment=1
        )

        # Add header
        elements.append(Paragraph(f"Account Statement", title_style))
        elements.append(Paragraph(f"{self.account.name}", subtitle_style))
        date_range = f"{self.filters.start_date.strftime('%B %d, %Y')} to {self.filters.end_date.strftime('%B %d, %Y')}"
        elements.append(Paragraph(f"Period: {date_range}", subtitle_style))
        elements.append(Spacer(1, 20))

        # Account summary
        summary_data = [
            ['Account Details', ''],
            ['Account Category:', self.account.account_type.title()],
            ['Currency:', self.account.currency],
            ['Total Income:', f"{self.account.currency} {self.summary['total_income']:,.2f}"],
            ['Total Expenses:', f"{self.account.currency} {self.summary['total_expenses']:,.2f}"],
            ['Net Balance:', f"{self.account.currency} {self.summary['balance']:,.2f}"]
        ]

        summary_table = Table(summary_data, colWidths=[2.5 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_HEADER),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, self.COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            # Color code income and expenses
            ('TEXTCOLOR', (1, 3), (1, 3), self.COLOR_INCOME),  # Income
            ('TEXTCOLOR', (1, 4), (1, 4), self.COLOR_EXPENSE),  # Expenses
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 30))

        # Transactions table
        elements.append(Paragraph("Transaction History", subtitle_style))

        # Table header and data
        trans_data = [['Date', 'Category', 'Tag', 'Description', 'Amount', 'Type']]
        for t in self.transactions:
            amount_str = f"{self.account.currency} {float(t.amount):,.2f}"
            trans_data.append([
                t.date.strftime('%Y-%m-%d'),
                t.category,
                t.tag,
                t.description,
                amount_str,
                t.transaction_type.capitalize()
            ])

        # Create transaction table with specific column widths
        trans_table = Table(trans_data, colWidths=[1 * inch, 1.5 * inch, 1 * inch, 2 * inch, 1.2 * inch, 1 * inch])

        # Basic table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, self.COLOR_BORDER),
            ('ALIGN', (-2, 1), (-2, -1), 'RIGHT'),  # Align amounts right
        ]

        # Add row-specific styles for income/expense
        for i, row in enumerate(trans_data[1:], 1):
            if row[-1] == 'Income':
                table_style.append(('TEXTCOLOR', (-2, i), (-2, i), self.COLOR_INCOME))
            else:
                table_style.append(('TEXTCOLOR', (-2, i), (-2, i), self.COLOR_EXPENSE))

            # Add alternating row colors
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa')))

        trans_table.setStyle(TableStyle(table_style))
        elements.append(trans_table)

        # Add page numbers
        def add_page_number(canvas, doc):
            page_num = canvas.getPageNumber()
            text = "Page %s" % page_num
            canvas.drawRightString(doc.pagesize[0] - 30, 30, text)

        # Build PDF
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        output.seek(0)
        return output

    def export(self):
        """Export report in specified format with proper filename"""
        output = None
        mimetype = None
        timestamp = datetime.now().strftime('%Y%m%d')

        if self.filters.format.lower() == 'xlsx':
            output = self.generate_excel()
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'spending_report_{timestamp}.xlsx'
        else:
            output = self.generate_pdf()
            mimetype = 'application/pdf'
            filename = f'spending_report_{timestamp}.pdf'

        # Ensure the output is at the start
        if output:
            output.seek(0)

        return output, mimetype, filename
