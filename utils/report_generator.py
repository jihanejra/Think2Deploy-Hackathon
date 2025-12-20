"""
Générateur de rapports PDF pour les évaluations de formation
"""
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import io
import base64  # Ajout de cet import
import tempfile
import streamlit as st

# Imports ReportLab
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas

def generate_pdf_report(df, output_path="rapport_evaluations.pdf"):
    """
    Génère un rapport PDF complet des évaluations
    """
    try:
        # Créer le document PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Styles
        styles = getSampleStyleSheet()
        story = []

        # Titre principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1f77b4'),
            alignment=1  # Centré
        )
        story.append(Paragraph("Rapport d'Analyse des Evaluations de Formation", title_style))
        story.append(Spacer(1, 20))

        # Date du rapport
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        story.append(Paragraph(f'Date de generation: {date_str}', styles['Normal']))
        story.append(Spacer(1, 30))

        # Section 1: Résumé exécutif
        story.append(Paragraph('1. Resume Executif', styles['Heading2']))
        story.append(Spacer(1, 10))

        # Calcul des métriques clés
        total_evaluations = len(df)

        # Taux de complétion
        if 'Évaluation_Complète' in df.columns:
            completed = df['Évaluation_Complète'].sum()
            completion_rate = (completed / total_evaluations) * 100
        else:
            completion_rate = 100

        # Scores moyens
        criteria = ['Satisfaction', 'Contenu', 'Logistique', 'Applicabilité']
        available_criteria = [c for c in criteria if c in df.columns]

        if available_criteria:
            avg_scores = {c: df[c].mean(skipna=True) for c in available_criteria}
            overall_avg = np.mean(list(avg_scores.values()))
        else:
            overall_avg = 0

        # Texte du résumé - CORRIGÉ : utilisation de quotes simples pour les f-strings
        summary_text = f"""
        Ce rapport analyse {total_evaluations} evaluations de formation. 
        Le taux de completion global est de {completion_rate:.1f}% et le score moyen 
        global est de {overall_avg:.2f}/5.
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))

        # Section 2: Métriques clés
        story.append(Paragraph('2. Indicateurs Cles de Performance', styles['Heading2']))
        story.append(Spacer(1, 10))

        # Tableau des métriques
        metrics_data = [
            ['Indicateur', 'Valeur', 'Cible'],
            ['Total evaluations', f'{total_evaluations:,}', 'N/A'],
            ['Taux de completion', f'{completion_rate:.1f}%', '≥95%'],
            ['Score moyen global', f'{overall_avg:.2f}/5', '≥4.0']
        ]

        if 'Évaluation_Complète' in df.columns:
            metrics_data.append(['Evaluations completes', f'{completed:,}', 'N/A'])

        # Créer la table
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(metrics_table)
        story.append(Spacer(1, 30))

        # Section 3: Recommandations
        story.append(Paragraph('3. Recommandations', styles['Heading2']))
        story.append(Spacer(1, 10))

        recommendations = [
            '1. Maintenir l\'excellence : Continuer les bonnes pratiques pour les formations avec scores eleves.',
            '2. Amelioration ciblee : Identifier les formations avec scores bas pour mise a niveau.',
            '3. Encourager la completion : Mettre en place des rappels pour les evaluations incompletes.',
            '4. Analyse trimestrielle : Generer ce rapport regulierement pour suivre les tendances.',
            '5. Formation des formateurs : Partager les meilleures pratiques entre formateurs performants.'
        ]

        for rec in recommendations:
            story.append(Paragraph(rec, styles['Normal']))
            story.append(Spacer(1, 5))

        # Section 4: Données détaillées (limitées)
        story.append(Paragraph('4. Echantillon des Donnees', styles['Heading2']))
        story.append(Spacer(1, 10))

        # Prendre un échantillon des colonnes principales
        sample_cols = []
        if 'Type de Formation' in df.columns:
            sample_cols.append('Type de Formation')
        if 'Note_Moyenne' in df.columns:
            sample_cols.append('Note_Moyenne')
        if 'Satisfaction' in df.columns:
            sample_cols.append('Satisfaction')
        if 'Date' in df.columns:
            sample_cols.append('Date')

        if sample_cols:
            sample_data = df[sample_cols].head(10)

            # Convertir en liste pour le tableau
            table_data = [sample_cols]  # En-têtes

            for _, row in sample_data.iterrows():
                row_data = []
                for col in sample_cols:
                    value = row[col]
                    if pd.isna(value):
                        row_data.append('N/A')
                    elif col == 'Date' and hasattr(value, 'strftime'):
                        row_data.append(value.strftime('%d/%m/%Y'))
                    elif col in ['Note_Moyenne', 'Satisfaction']:
                        row_data.append(f'{float(value):.2f}')
                    else:
                        row_data.append(str(value))
                table_data.append(row_data)

            # Créer le tableau
            sample_table = Table(table_data)
            sample_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))

            story.append(sample_table)

        # Pied de page
        story.append(Spacer(1, 30))
        story.append(Paragraph(f'Rapport genere automatiquement - {total_evaluations} evaluations analysees',
                             ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
                                          textColor=colors.grey, alignment=1)))

        # Générer le PDF
        doc.build(story)

        return output_path

    except Exception as e:
        print(f'Erreur generation PDF: {e}')
        import traceback
        print(traceback.format_exc())
        return None

def generate_streamlit_report(df):
    """
    Version pour Streamlit avec téléchargement
    """
    st.markdown('### Generation de Rapport PDF')

    # Options simples
    col1, col2 = st.columns(2)

    with col1:
        report_name = st.text_input('Nom du rapport:',
                                   value=f'rapport_evaluations_{datetime.now().strftime("%Y%m%d")}')

    with col2:
        include_sample = st.checkbox('Inclure echantillon donnees', value=True)

    # Bouton de génération
    if st.button('Generer le rapport PDF', type='primary'):
        with st.spinner('Generation du rapport en cours...'):
            try:
                # Créer un fichier temporaire
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    pdf_path = tmp_file.name

                # Générer le PDF
                output_path = generate_pdf_report(df, pdf_path)

                if output_path:
                    # Lire le fichier PDF
                    with open(output_path, 'rb') as f:
                        pdf_bytes = f.read()

                    # Bouton de téléchargement
                    st.success('Rapport genere avec succes!')

                    st.download_button(
                        label='Telecharger le PDF',
                        data=pdf_bytes,
                        file_name=f'{report_name}.pdf',
                        mime='application/pdf',
                        key='download_pdf_report'
                    )

                    # Aperçu (première page)
                    if st.checkbox('Afficher l\'aperçu'):
                        try:
                            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                            pdf_display = f'''
                            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
                                <iframe src="data:application/pdf;base64,{base64_pdf}" 
                                        width="100%" 
                                        height="500" 
                                        type="application/pdf">
                                </iframe>
                            </div>
                            '''
                            st.markdown(pdf_display, unsafe_allow_html=True)
                        except:
                            st.info('Aperçu non disponible')

                else:
                    st.error('Erreur lors de la generation du rapport')

            except Exception as e:
                st.error(f'Erreur: {e}')
                st.info('Assurez-vous que reportlab est installe: `pip install reportlab`')