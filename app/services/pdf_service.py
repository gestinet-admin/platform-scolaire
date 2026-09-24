from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from app.models import Inscription, Eleve

class PDFService:
    """Service de génération PDF"""
    
    @staticmethod
    def generer_liste_classe(etablissement_name, classe, eleves):
        """Générer PDF liste classe"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Titre
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1F4E78'), alignment=TA_CENTER, fontName='Helvetica-Bold')
        story.append(Paragraph(f'{etablissement_name}', title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Classe
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, fontName='Helvetica-Bold')
        story.append(Paragraph(f'Liste Classe: {classe}', subtitle_style))
        story.append(Paragraph(f'Date: {datetime.now().strftime("%d/%m/%Y")}', styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Table élèves
        data = [['N°', 'Nom', 'Prénom', 'Date Naissance', 'Parent']]
        for i, eleve in enumerate(eleves, 1):
            data.append([
                str(i),
                eleve.nom or '',
                eleve.prenom or '',
                eleve.date_naissance.strftime('%d/%m/%Y') if eleve.date_naissance else '',
                eleve.parent.email if eleve.parent else ''
            ])
        
        table = Table(data, colWidths=[0.8*inch, 1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E78')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        story.append(Paragraph(f'PlatformScolaire © {datetime.now().year}', footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generer_bulletin(eleve, inscription):
        """Générer bulletin élève"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        story = []
        
        # En-tête
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1F4E78'), alignment=TA_CENTER, fontName='Helvetica-Bold')
        story.append(Paragraph('BULLETIN SCOLAIRE', title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Infos élève
        info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=11)
        story.append(Paragraph(f'<b>Élève:</b> {eleve.nom_complet()}', info_style))
        story.append(Paragraph(f'<b>Classe:</b> {inscription.annee_scolaire}', info_style))
        story.append(Paragraph(f'<b>Année:</b> {datetime.now().year}', info_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Frais
        frais_restants = (inscription.frais_total or 0) - (inscription.frais_payes or 0)
        story.append(Paragraph(f'<b>Situation Financière:</b>', ParagraphStyle('Bold', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')))
        story.append(Paragraph(f'• Frais total: {inscription.frais_total} FCFA', info_style))
        story.append(Paragraph(f'• Frais payés: {inscription.frais_payes} FCFA', info_style))
        story.append(Paragraph(f'• <b>Reste à payer: {frais_restants} FCFA</b>', info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Signature
        story.append(Spacer(1, 0.5*inch))
        sig_style = ParagraphStyle('Sig', parent=styles['Normal'], fontSize=10)
        story.append(Paragraph('Directeur: ________________     Date: ________________', sig_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generer_recu_paiement(paiement, inscription, eleve):
        """Générer reçu paiement"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        story = []
        
        # En-tête
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#2E7D32'), alignment=TA_CENTER, fontName='Helvetica-Bold')
        story.append(Paragraph('✓ REÇU DE PAIEMENT', title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Info reçu
        info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=11)
        story.append(Paragraph(f'<b>N° Reçu:</b> REC-{paiement.id:06d}', info_style))
        story.append(Paragraph(f'<b>Date:</b> {paiement.date_paiement.strftime("%d/%m/%Y %H:%M")}', info_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Info élève
        story.append(Paragraph(f'<b>Élève:</b> {eleve.nom_complet()}', info_style))
        story.append(Paragraph(f'<b>Classe:</b> {inscription.annee_scolaire}', info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Détails paiement
        story.append(Paragraph(f'<b>Montant payé:</b> {paiement.montant} FCFA', ParagraphStyle('Amount', parent=styles['Normal'], fontSize=14, fontName='Helvetica-Bold', textColor=colors.HexColor('#2E7D32'))))
        story.append(Paragraph(f'<b>Méthode:</b> {paiement.methode}', info_style))
        if paiement.reference:
            story.append(Paragraph(f'<b>Référence:</b> {paiement.reference}', info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Paragraph('Ce reçu est valide et certifié', ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Oblique')))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
