import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os
import qrcode
from io import BytesIO
import smtplib
from email.message import EmailMessage

# Fire code dropdowns
uae_fire_codes = [
    "UAE-FC 1: Fire Alarm Design Requirements",
    "UAE-FC 2: Fire Extinguisher Placement Guide",
    "UAE-FC 3: Emergency Exit Specifications"
]
nfpa_codes = [
    "NFPA 1: Fire Code Overview",
    "NFPA 13: Sprinkler System Standards",
    "NFPA 70: Electrical Code"
]

# Extracted checklist from PDF
checklist_data = {
    "FIRE DETECTION & ALARM SYSTEM (FDAS)": [
        "Main Panel – Working / Not working",
        "Batteries Available – Yes / No",
        "Detectors installed – Yes / No",
        "Manual Call Points (MCPs) – Installed & working / Not working",
        "Fire Alarm Hooter / Bell – Installed & working / Not working",
        "Cables & Conduits are secured",
        "Zone chart fixed"
    ],
    "EMERGENCY & EXIT LIGHTS": [
        "Exit Lights Installed",
        "Emergency Lights Installed",
        "Working with battery backup"
    ],
    "FIRE EXTINGUISHERS": [
        "Installed in required areas",
        "Proper types (CO2, DCP, Water, Foam) as per hazard",
        "Accessible, visible, labeled, sealed",
        "Annual maintenance done"
    ],
    "FIRE HOSE REELS": [
        "Installed near exit doors",
        "Hose reel cabinet is accessible",
        "No leakage or damage in hose & nozzle",
        "Water pressure available"
    ],
    "FIRE PUMP ROOM": [
        "Main & standby pumps operational",
        "Diesel engine operational",
        "Pump room accessible & clean",
        "Pressure gauge & valves functional"
    ],
    "SPRINKLER SYSTEM": [
        "Sprinklers installed as per coverage",
        "Sprinklers not painted or blocked",
        "Control valves open & locked",
        "Alarm valves functioning"
    ],
    "FIRE EXIT / STAIRCASE": [
        "Exit doors not locked/blocked",
        "Staircases clear from obstruction",
        "Emergency lights in exit path",
        "Exit signs illuminated"
    ],
    "GAS CYLINDERS / LPG AREA": [
        "Installed in well-ventilated area",
        "Regulators in good condition",
        "No leakage detected",
        "Safety signage available"
    ],
    "BUILDING GENERAL": [
        "No combustible waste stored near exits",
        "Electrical panels covered",
        "No exposed live wires",
        "Proper housekeeping maintained"
    ]
}

st.set_page_config(page_title="Fire Safety Inspection Report", layout="wide")

col_logo, col_title, col_image = st.columns([1, 2, 1])
with col_logo:
    company_logo = st.file_uploader("Upload Company Logo", type=["jpg", "jpeg", "png"])
with col_title:
    st.title("Fire Safety Inspection Report")
with col_image:
    site_image = st.file_uploader("Upload Site Image", type=["jpg", "jpeg", "png"])

st.header("📤 Uploads")
client_name = st.text_input("Client Name")
location = st.text_input("Location")
inspection_date = st.date_input("Inspection Date")

st.header("Inspection Checklist")
for section, questions in checklist_data.items():
    st.subheader(section)
    for i, q in enumerate(questions):
        col1, col2, col3, col4, col5 = st.columns([3, 4, 2, 2, 3])
        with col1:
            st.markdown(f"**{q}**")
            status = st.radio("Status", ["Yes", "No", "N/A"], key=f"status_{section}_{i}", horizontal=True)
        with col2:
            note = st.text_area("Observations / Notes", height=150, key=f"note_{section}_{i}")
        with col3:
            uae_code = st.selectbox("UAE Code", uae_fire_codes, key=f"uae_{section}_{i}")
        with col4:
            nfpa_code = st.selectbox("NFPA Code", nfpa_codes, key=f"nfpa_{section}_{i}")
        with col5:
            uploaded_file = st.file_uploader("Media", type=["jpg", "jpeg", "png"], key=f"media_{section}_{i}")

inspector_name = st.text_input("Inspector Name")
signature_image = st.file_uploader("Upload Signature", type=["jpg", "jpeg", "png"], key="signature")
email_to = st.text_input("Email the report to")
filename = "inspection_report.pdf"

# PDF generation, email, and download code remains unchanged


