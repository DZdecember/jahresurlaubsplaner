import streamlit as st
import datetime
import numpy as np
from weasyprint import HTML

# Configure Page Layout
st.set_page_config(page_title="Jahresurlaubsplaner", page_icon="📅", layout="wide")

st.title("📅 Jahresurlaubsplan / -antrag App")
st.markdown("Füllen Sie Ihre Urlaubsplanung digital aus. Die App berechnet die Arbeitstage automatisch und erstellt einen fertigen PDF-Urlaubsantrag für Ihren Chef.")

# Sidebar for Employee Info & Entitlement Calculations
st.sidebar.header("👤 Mitarbeiterinformationen")
name = st.sidebar.text_input("Name des Mitarbeiters", placeholder="Max Mustermann")
position = st.sidebar.text_input("Berufsbezeichnung / Position", placeholder="Software Entwickler")
department = st.sidebar.text_input("Abteilung", placeholder="IT")
year = st.sidebar.number_input("Kalenderjahr", min_value=2026, max_value=2035, value=2026)

st.sidebar.markdown("---")
st.sidebar.header("📊 Urlaubsanspruch")
# Input for total vacation days the employer grants
total_allowance = st.sidebar.number_input("Gesamtanspruch (Tage im Jahr)", min_value=0, max_value=100, value=30)

# Main Area for Vacation Blocks
st.header("✈️ Geplante Urlaubszeiträume")
st.caption("Wochenenden werden automatisch aus der Berechnung der Arbeitstage abgezogen.")

# Setup columns for grid layout input
cols = st.columns([1, 2, 2, 2])
with cols[0]: st.markdown("**Block**")
with cols[1]: st.markdown("**Urlaubsbeginn (Erster Tag)**")
with cols[2]: st.markdown("**Urlaubsende (Letzter Tag)**")
with cols[3]: st.markdown("**Betroffene(r) Monat(e)**")

blocks_data = []
total_days = 0

# Generate 6 blocks of dynamic inputs
for i in range(1, 7):
    cols_input = st.columns([1, 2, 2, 2])
    
    with cols_input[0]:
        st.markdown(f"<div style='padding-top:10px; font-weight:bold;'>{i}</div>", unsafe_allow_html=True)
        
    with cols_input[1]:
        start = st.date_input(f"Beginn {i}", value=None, key=f"start_{i}", label_visibility="collapsed")
        
    with cols_input[2]:
        end = st.date_input(f"Ende {i}", value=None, key=f"end_{i}", label_visibility="collapsed")
        
    with cols_input[3]:
        default_month = ""
        if start:
            months_de = ["", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
            default_month = months_de[start.month]
            if end and end.month != start.month:
                default_month += f" / {months_de[end.month]}"
                
        month = st.text_input(f"Monat {i}", value=default_month, key=f"month_{i}", label_visibility="collapsed")
    
    # Calculate business days (excluding weekends) live!
    block_days = 0
    if start and end:
        if start <= end:
            block_days = int(np.busday_count(np.datetime64(start), np.datetime64(end)))
            if np.is_busday(np.datetime64(end)):
                block_days += 1
        else:
            st.error(f"Fehler in Block {i}: Das Ende-Datum liegt vor dem Start-Datum!")
            
    blocks_data.append({
        "start": start.strftime('%d.%m.%Y') if start else "",
        "end": end.strftime('%d.%m.%Y') if end else "",
        "month": month,
        "days": block_days if block_days > 0 else ""
    })
    total_days += block_days

# Dynamic Balance Calculation
remaining_days = total_allowance - total_days

# Summary Display UI Cards
st.markdown("---")
st.subheader("📊 Urlaubsbilanz Übersicht")
sum_col1, sum_col2, sum_col3 = st.columns(3)
with sum_col1:
    st.metric("Gesamtanspruch", f"{total_allowance} Tage")
with sum_col2:
    st.metric("Beantragte Urlaubstage", f"{total_days} Tage", delta=f"-{total_days}" if total_days > 0 else None)
with sum_col3:
    if remaining_days >= 0:
        st.metric("Verbleibender Resturlaub", f"{remaining_days} Tage")
    else:
        st.metric("⚠️ Anspruch überschritten!", f"{remaining_days} Tage", delta=remaining_days)

# Function to generate HTML template populated with runtime app data
def generate_html():
    rows_html = ""
    for idx, b in enumerate(blocks_data, 1):
        rows_html += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; background-color: #fafbfc; border: 1px solid #dcdde1; padding: 10px 8px;">{idx}</td>
            <td style="border: 1px solid #dcdde1; padding: 10px 8px; height: 38px;">{b['start']}</td>
            <td style="border: 1px solid #dcdde1; padding: 10px 8px;">{b['end']}</td>
            <td style="border: 1px solid #dcdde1; padding: 10px 8px;">{b['month']}</td>
            <td style="border: 1px solid #dcdde1; padding: 10px 8px; text-align: right; font-weight: bold;">{b['days']}</td>
        </tr>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 15mm 12mm; background-color: #fcfdfe; }}
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2c3e50; font-size: 10.5pt; line-height: 1.4; }}
            .header-container {{ border-bottom: 3px solid #2b5c8f; padding-bottom: 10px; margin-bottom: 20px; }}
            .form-title {{ font-size: 22pt; color: #1e3d59; font-weight: bold; text-transform: uppercase; margin: 0; }}
            .section-title {{ font-size: 12pt; font-weight: bold; color: #1e3d59; background-color: #eaeff5; padding: 5px 10px; margin-top: 20px; margin-bottom: 12px; border-left: 5px solid #2b5c8f; }}
            .form-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
            .form-table td {{ padding: 8px 6px; vertical-align: middle; }}
            .label {{ font-weight: 600; color: #34495e; width: 25%; }}
            .input-field {{ border-bottom: 1px solid #bdc3c7; height: 28px; font-weight: bold; color: #2c3e50; }}
            .schedule-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            .schedule-table th {{ background-color: #2b5c8f; color: white; font-weight: bold; font-size: 10pt; text-align: left; padding: 8px; border: 1px solid #2b5c8f; }}
            .summary-box {{ background-color: #f7f9fa; border: 1px solid #dcdde1; border-radius: 4px; padding: 12px; margin-top: 15px; }}
            .checkbox-container {{ padding: 4px 0; }}
            .checkbox-box {{ display: inline-block; width: 13px; height: 13px; border: 1px solid #7f8c8d; margin-right: 6px; vertical-align: middle; }}
            .signature-table {{ width: 100%; border-collapse: separate; border-spacing: 20px 0; margin-top: 20px; }}
            .signature-line {{ border-top: 1px solid #2c3e50; margin-top: 40px; padding-top: 4px; font-size: 9.5pt; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="header-container">
            <h1 class="form-title">Jahresurlaubsplan / -antrag</h1>
            <p style="margin:5px 0 0 0; color:#7f8c8d; font-size:10pt;">Bitte nutzen Sie dieses Formular zur vorausschauenden Planung Ihrer Urlaubszeiten.</p>
        </div>

        <div class="section-title">Mitarbeiterinformationen</div>
        <table class="form-table">
            <tr>
                <td class="label">Name des Mitarbeiters:</td>
                <td class="input-field" style="width: 28%;">{name}</td>
                <td style="width: 4%;"></td>
                <td class="label">Berufsbezeichnung / Position:</td>
                <td class="input-field" style="width: 28%;">{position}</td>
            </tr>
            <tr>
                <td class="label">Abteilung:</td>
                <td class="input-field">{department}</td>
                <td></td>
                <td class="label">Kalenderjahr für Urlaubsplanung:</td>
                <td class="input-field">{year}</td>
            </tr>
        </table>

        <div class="section-title">Geplante Urlaubszeiträume</div>
        <table class="schedule-table">
            <thead>
                <tr>
                    <th style="width: 6%; text-align: center;">Block</th>
                    <th style="width: 24%;">Urlaubsbeginn (Erster Tag)</th>
                    <th style="width: 24%;">Urlaubsende (Letzter Tag)</th>
                    <th style="width: 26%;">Betroffene(r) Monat(e)</th>
                    <th style="width: 20%; text-align: right;">Beantragte Arbeitstage</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <div class="summary-box">
            <table style="width: 100%; border-collapse: collapse; font-size: 11pt;">
                <tr>
                    <td style="width: 30%; font-weight: bold; padding: 6px;">Gesamtanspruch des Jahres:</td>
                    <td style="width: 10%; border: 1px solid #bdc3c7; background-color: #fff; text-align: center; font-weight: bold;">{total_allowance} Tage</td>
                    <td style="width: 5%;"></td>
                    <td style="width: 30%; font-weight: bold; padding: 6px; color: #2b5c8f;">Beantragte Urlaubstage gesamt:</td>
                    <td style="width: 10%; border: 2px solid #2b5c8f; background-color: #fff; text-align: center; font-weight: bold; color: #2b5c8f;">{total_days} Tage</td>
                    <td style="width: 5%;"></td>
                    <td style="width: 30%; font-weight: bold; padding: 6px; color: #27ae60;">Verbleibender Resturlaub:</td>
                    <td style="width: 10%; border: 2px solid #27ae60; background-color: #fff; text-align: center; font-weight: bold; color: #27ae60;">{remaining_days} Tage</td>
                </tr>
            </table>
        </div>

        <div class="section-title">Genehmigung & Unterschriften</div>
        <table class="signature-table">
            <tr>
                <td><div class="signature-line">Unterschrift Mitarbeiter</div></td>
                <td><div class="signature-line">Datum</div></td>
            </tr>
        </table>

        <div style="margin-top: 30px; background-color: #fafbfc; border: 1px dashed #bdc3c7; padding: 12px; border-radius: 4px;">
            <div style="font-weight: bold; color: #1e3d59; margin-bottom: 10px;">Nur vom Management / der Personalabteilung auszufüllen</div>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="width: 45%; vertical-align: top;">
                        <div class="checkbox-container"><div class="checkbox-box"></div> <span style="font-size:10pt;">Gesamtplanung genehmigt</span></div>
                        <div class="checkbox-container" style="margin-top: 4px;"><div class="checkbox-box"></div> <span style="font-size:10pt;">Genehmigt mit Änderungen</span></div>
                    </td>
                    <td style="width: 55%; vertical-align: top;">
                        <div class="signature-line" style="margin-top: 10px;">Unterschrift Vorgesetzter / Manager</div>
                        <div class="signature-line" style="margin-top: 20px;">Datum</div>
                    </td>
                </tr>
            </table>
        </div>
    </body>
    </html>
    """
    return html_template

# PDF Generation Trigger
if st.button("🚀 Offizielles PDF-Dokument generieren"):
    with st.spinner("Erstelle PDF..."):
        try:
            final_html = generate_html()
            pdf_bytes = HTML(string=final_html).write_pdf()
            
            st.download_button(
                label="📥 Bereitgestellten Urlaubsantrag herunterladen (PDF)",
                data=pdf_bytes,
                file_name=f"Urlaubsantrag_{name.replace(' ', '_') if name else 'Mitarbeiter'}_{year}.pdf",
                mime="application/pdf"
            )
            st.success("Erfolgreich generiert! Klicken Sie oben, um die PDF herunterzuladen.")
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")
