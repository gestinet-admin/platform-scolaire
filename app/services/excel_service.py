from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
from io import BytesIO

class ExcelService:
    """Service de génération Excel"""
    
    @staticmethod
    def generer_rapport_frais(etablissement_name, inscriptions):
        """Générer rapport frais Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Frais Scolaires"
        
        # En-tête
        ws['A1'] = etablissement_name
        ws['A1'].font = Font(size=14, bold=True, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
        ws.merge_cells('A1:E1')
        
        ws['A2'] = f'Rapport Frais - {datetime.now().strftime("%d/%m/%Y")}'
        ws['A2'].font = Font(size=11, bold=True)
        ws.merge_cells('A2:E2')
        
        # Headers
        headers = ['N°', 'Élève', 'Classe', 'Frais Total', 'Frais Payés', 'Reste', 'Statut']
        header_fill = PatternFill(start_color='2E7D32', end_color='2E7D32', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Données
        row = 5
        total_frais = 0
        total_payes = 0
        
        for i, inscription in enumerate(inscriptions, 1):
            frais_restants = (inscription.frais_total or 0) - (inscription.frais_payes or 0)
            statut = '⚠️ Retard' if frais_restants > 0 else '✓ Payé'
            
            ws.cell(row=row, column=1).value = i
            ws.cell(row=row, column=2).value = inscription.eleve.nom_complet()
            ws.cell(row=row, column=3).value = inscription.annee_scolaire
            ws.cell(row=row, column=4).value = inscription.frais_total or 0
            ws.cell(row=row, column=5).value = inscription.frais_payes or 0
            ws.cell(row=row, column=6).value = frais_restants
            ws.cell(row=row, column=7).value = statut
            
            total_frais += inscription.frais_total or 0
            total_payes += inscription.frais_payes or 0
            row += 1
        
        # Totaux
        row += 1
        ws.cell(row=row, column=2).value = 'TOTAUX'
        ws.cell(row=row, column=2).font = Font(bold=True)
        ws.cell(row=row, column=4).value = total_frais
        ws.cell(row=row, column=4).font = Font(bold=True)
        ws.cell(row=row, column=5).value = total_payes
        ws.cell(row=row, column=5).font = Font(bold=True)
        ws.cell(row=row, column=6).value = total_frais - total_payes
        ws.cell(row=row, column=6).font = Font(bold=True)
        
        # Largeurs colonnes
        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15
        ws.column_dimensions['G'].width = 15
        
        # Format monnaie
        for row in ws.iter_rows(min_row=5, max_row=row, min_col=4, max_col=6):
            for cell in row:
                cell.number_format = '#,##0'
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generer_liste_eleves(etablissement_name, eleves):
        """Générer liste élèves Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Élèves"
        
        # En-tête
        ws['A1'] = etablissement_name
        ws['A1'].font = Font(size=14, bold=True, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
        ws.merge_cells('A1:F1')
        
        # Headers
        headers = ['N°', 'Nom', 'Prénom', 'Classe', 'Date Naissance', 'Parent']
        header_fill = PatternFill(start_color='2E7D32', end_color='2E7D32', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
        
        # Données
        for row, eleve in enumerate(eleves, 4):
            ws.cell(row=row, column=1).value = row - 3
            ws.cell(row=row, column=2).value = eleve.nom
            ws.cell(row=row, column=3).value = eleve.prenom
            ws.cell(row=row, column=4).value = eleve.classe_actuelle
            ws.cell(row=row, column=5).value = eleve.date_naissance
            ws.cell(row=row, column=6).value = eleve.parent.email if eleve.parent else ''
        
        # Largeurs
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            ws.column_dimensions[col].width = 18
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
