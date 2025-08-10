"""Export election results to JSON, CSV and PDF.
This module will attempt to use reportlab for PDF. If not present it will still export JSON/CSV.
"""
import os
import json
import datetime
from .db import DatabaseManager

class ResultsExporter:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def export_results(self, election_id: int, output_dir: str = "results"):
        os.makedirs(output_dir, exist_ok=True)

        election = self.db.execute("SELECT name FROM Elections WHERE id = ?", (election_id,), fetch=True)
        if not election:
            raise ValueError("Election not found")

        election_name = election[0][0]
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        rows = self.db.execute('''
            SELECT c.name, COUNT(v.id) as votes, c.symbol_path
            FROM Candidates c
            LEFT JOIN Votes v ON c.id = v.candidate_id
            WHERE c.election_id = ?
            GROUP BY c.id, c.name, c.symbol_path
            ORDER BY votes DESC
        ''', (election_id,), fetch=True)

        total_votes = sum(r[1] for r in rows)

        results_data = []
        for name, votes, symbol_path in rows:
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            results_data.append({
                'candidate': name,
                'votes': votes,
                'percentage': round(percentage, 2),
                'symbol_path': symbol_path
            })

        base = f"{election_name}_{ts}"
        json_path = os.path.join(output_dir, base + ".json")
        csv_path = os.path.join(output_dir, base + ".csv")
        pdf_path = os.path.join(output_dir, base + ".pdf")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'election_name': election_name,
                'total_votes': total_votes,
                'timestamp': ts,
                'results': results_data
            }, f, indent=2)

        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write('Candidate,Votes,Percentage\n')
            for r in results_data:
                f.write(f"{r['candidate']},{r['votes']},{r['percentage']}\n")

        try:
            self._create_pdf(election_name, results_data, total_votes, pdf_path, ts)
            pdf_created = pdf_path
        except ImportError:
            txt_path = pdf_path.replace('.pdf', '.txt')
            self._create_text_report(election_name, results_data, total_votes, txt_path, ts)
            pdf_created = txt_path
        except Exception as e:
            txt_path = pdf_path.replace('.pdf', '.txt')
            self._create_text_report(election_name, results_data, total_votes, txt_path, ts)
            pdf_created = txt_path

        return json_path, csv_path, pdf_created

    def _create_pdf(self, election_name, results_data, total_votes, out_path, timestamp):
        """Create PDF using ReportLab"""
        print("[DEBUG] Starting PDF creation...")

        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from PIL import Image as PILImage

        doc = SimpleDocTemplate(out_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        print("[DEBUG] Adding title section...")
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        story.append(Paragraph("ELECTION RESULTS", title_style))

        details_style = ParagraphStyle(
            'Details',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"<b>Election:</b> {election_name}", details_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", details_style))
        story.append(Spacer(1, 30))

        print("[DEBUG] Building results table...")
        table_data = [['Rank', 'Name', 'Votes', 'Percentage', 'Symbol']]
        for i, result in enumerate(results_data, 1):
            symbol_element = self._create_symbol_for_pdf(result.get('symbol_path'))
            table_data.append([
                str(i),
                result['candidate'][:35],
                str(result['votes']),
                f"{result['percentage']}%",
                symbol_element
            ])

        table = Table(
            table_data,
            colWidths=[0.6*inch, 3*inch, 1.2*inch, 1*inch, 1.5*inch], 
            rowHeights=[None] + [0.8*inch] * len(results_data)
        )
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(table)

        story.append(Spacer(1, 40))
        totals_style = ParagraphStyle(
            'Totals',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_LEFT,
            leftIndent=50
        )
        story.append(Paragraph("Total Voters ............................................", totals_style))
        story.append(Paragraph("Total Ballots Cast ............................................", totals_style))

        print(f"[DEBUG] Saving PDF to: {out_path}")
        doc.build(story)
        print("[DEBUG] PDF creation complete.")

    def _create_symbol_for_pdf(self, symbol_path):
        """Create a ReportLab Image element for the symbol, or return placeholder text"""
        try:
            from reportlab.platypus import Image
            from reportlab.lib.units import inch
            if symbol_path and os.path.exists(symbol_path):
                print(f"[DEBUG] Adding symbol image: {symbol_path}")
                return Image(symbol_path, width=0.6*inch, height=0.4*inch)
            else:
                print("[DEBUG] No symbol found, using placeholder text.")
                return "No Symbol"
        except Exception as e:
            print(f"[DEBUG] Symbol load error: {e}")
            return "Symbol Error"

    def _create_text_report(self, election_name, results_data, total_votes, out_path, timestamp):
        """Create text-based report as fallback when PDF creation fails"""
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ELECTION RESULTS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Election: {election_name}\n")
            f.write(f"Total Votes: {total_votes}\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("RESULTS:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Rank':<6} {'Candidate':<30} {'Votes':<8} {'Percentage':<12}\n")
            f.write("-" * 60 + "\n")
            
            for i, r in enumerate(results_data, 1):
                f.write(f"{i:<6} {r['candidate']:<30} {r['votes']:<8} {r['percentage']:<12}%\n")
            
            f.write("-" * 60 + "\n")
            f.write(f"\nNote: This is a text report. Install 'reportlab' package for PDF generation.\n")
            f.write("Run: pip install reportlab\n")