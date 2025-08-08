import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os

# Your full checklist
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
st.title("Fire Safety Inspection Report")

st.header("📤 Uploads")
client_name = st.text_input("Client Name")
location = st.text_input("Location")
inspection_date = st.date_input("Inspection Date")

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

if st.button("Generate PDF Report"):
    filename = "inspection_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Header
    story.append(Paragraph("Fire Safety Inspection Report", styles["Title"]))
    story.append(Paragraph(f"Client Name: {client_name}", styles["Normal"]))
    story.append(Paragraph(f"Location: {location}", styles["Normal"]))
    story.append(Paragraph(f"Inspection Date: {inspection_date}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Inspector info
    inspector_name = st.text_input("Inspector Name")
    signature_image = st.file_uploader("Upload Signature", type=["png", "jpg", "jpeg"])

    # Checklist
    for section, questions in checklist_data.items():
        story.append(Paragraph(f"{section}", styles["Heading2"]))
        story.append(Spacer(1, 5))
        for i, q in enumerate(questions):
            status = st.session_state.get(f"status_{section}_{i}", "")
            note = st.session_state.get(f"note_{section}_{i}", "")
            image = st.session_state.get(f"media_{section}_{i}", None)

            story.append(Paragraph(f"<b> {q}</b>", styles["Normal"]))
            story.append(Paragraph(f"🟢 Status: <i>{status}</i>", styles["Normal"]))
            story.append(Paragraph(f"📝 Comment: <i>{note}</i>", styles["Normal"]))

            if image:
                img_path = f"temp_{q.replace(' ', '_')}.jpg"
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())
                story.append(RLImage(img_path, width=200))
                os.remove(img_path)

            story.append(Spacer(1, 15))

# Add inspector name and signature to the report
story.append(Spacer(1, 20))
story.append(Paragraph(f"Inspector Name: <b>{inspector_name}</b>", styles["Normal"]))

if signature_image is not None:
    sig_path = "temp_signature.jpg"
    with open(sig_path, "wb") as f:
        f.write(signature_image.read())
    story.append(Spacer(1, 10))
    story.append(Paragraph("Signature:", styles["Normal"]))
    story.append(RLImage(sig_path, width=100))
    os.remove(sig_path)

# Build the final PDF including inspector info
doc.build(story)

with open(filename, "rb") as f:
    st.download_button("Download PDF Report", f, file_name=filename)


    with open(filename, "rb") as f:
        st.download_button("Download PDF Report", f, file_name=filename)

