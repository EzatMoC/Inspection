import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os

# Full Fire Safety Checklist
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

# Upload Company Logo and Site Image
col_logo, col_site = st.columns([1, 1])
with col_logo:
    st.markdown("**Upload Company Logo**")
    company_logo = st.file_uploader(" ", type=["jpg", "jpeg", "png"], key="company_logo")
with col_site:
    st.markdown("**Upload Site Image**")
    site_image = st.file_uploader("  ", type=["jpg", "jpeg", "png"], key="site_image")

# Preview Images (optional)
col1, col2 = st.columns([1, 1])
if company_logo:
    with col1:
        st.image(company_logo, width=150, caption="Company Logo")
if site_image:
    with col2:
        st.image(site_image, width=200, caption="Site Image")

# Main Info
st.title("Fire Safety Inspection Report")
st.header("📤 Uploads")
client_name = st.text_input("Client Name")
location = st.text_input("Location")
inspection_date = st.date_input("Inspection Date")
inspector_name = st.text_input("Inspector Name")
signature_image = st.file_uploader("Upload Inspector Signature", type=["jpg", "jpeg", "png"])

# Checklist Inputs
st.header("Sample Checklist")
for section, questions in checklist_data.items():
    st.subheader(f"{section}")
    for i, q in enumerate(questions):
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            st.markdown(f"**{q}**")
            status = st.radio("Status", ["Yes", "No", "N/A"], key=f"status_{section}_{i}", horizontal=True)
        with col2:
            note = st.text_area("Observations / Notes", height=150, key=f"note_{section}_{i}")
        with col3:
            uploaded_file = st.file_uploader("Media", type=["jpg", "jpeg", "png"], key=f"media_{section}_{i}")

# Generate PDF
if st.button("Generate PDF Report"):
    filename = "inspection_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Add company logo (left) and site image (right)
    logo_path, site_path = None, None
    image_row = []

    if company_logo:
        logo_path = "temp_logo.jpg"
        with open(logo_path, "wb") as f:
            f.write(company_logo.read())
        image_row.append(RLImage(logo_path, width=100))
    else:
        image_row.append(Spacer(1, 1))

    if site_image:
        site_path = "temp_site.jpg"
        with open(site_path, "wb") as f:
            f.write(site_image.read())
        image_row.append(RLImage(site_path, width=120))
    else:
        image_row.append(Spacer(1, 1))

    story.append(Table([image_row], colWidths=[250, 250]))
    story.append(Spacer(1, 10))

    # Header Info
    story.append(Paragraph("Fire Safety Inspection Report", styles["Title"]))
    story.append(Paragraph(f"Client Name: {client_name}", styles["Normal"]))
    story.append(Paragraph(f"Location: {location}", styles["Normal"]))
    story.append(Paragraph(f"Inspection Date: {inspection_date}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Checklist
    for section, questions in checklist_data.items():
        story.append(Paragraph(f"{section}", styles["Heading2"]))
        story.append(Spacer(1, 5))
        for i, q in enumerate(questions):
            status = st.session_state._

