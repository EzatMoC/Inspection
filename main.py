import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os

# Fire Codes
uae_fire_codes = {
    "UAE 3.1.1": "Emergency exits must be illuminated.",
    "UAE 4.5.2": "Fire extinguishers must be accessible and labeled.",
    "UAE 7.2.3": "Electrical panels must be covered.",
}
nfpa_codes = {
    "NFPA 101": "Life Safety Code – exit access, lighting, signage.",
    "NFPA 10": "Standard for portable fire extinguishers.",
    "NFPA 72": "National Fire Alarm and Signaling Code.",
}

# Checklist
checklist_data = {
    "FIRE DETECTION & ALARM SYSTEM (FDAS)": [
        "Main Panel – Working / Not working",
        "Batteries Available – Yes / No",
        "Detectors installed – Yes / No",
    ],
    "EMERGENCY & EXIT LIGHTS": [
        "Exit Lights Installed",
        "Emergency Lights Installed"
    ]
}

st.set_page_config(page_title="Fire Safety Inspection Report", layout="wide")

# Uploads
logo = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])
site_image = st.file_uploader("Upload Site Image", type=["png", "jpg", "jpeg"])

# Layout for logo + site image
col_left, col_right = st.columns(2)
with col_left:
    if logo:
        st.image(logo, width=150)
with col_right:
    if site_image:
        st.image(site_image, width=150)

st.title("Fire Safety Inspection Report")

client_name = st.text_input("Client Name")
location = st.text_input("Location")
inspection_date = st.date_input("Inspection Date")
inspector_name = st.text_input("Inspector Name")
signature_image = st.file_uploader("Upload Signature", type=["png", "jpg", "jpeg"])

# Checklist input
st.header("Checklist")
for section, questions in checklist_data.items():
    st.subheader(section)
    for i, q in enumerate(questions):
        st.markdown(f"**{q}**")
        col1, col2, col3 = st.columns([1.5, 3, 1.5])
        with col1:
            st.radio("Status", ["Yes", "No", "N/A"], key=f"status_{section}_{i}", horizontal=True)
            st.selectbox("UAE Code", [""] + [f"{k} - {v}" for k, v in uae_fire_codes.items()],
                         key=f"uae_{section}_{i}")
        with col2:
            st.text_area("Observations", key=f"note_{section}_{i}")
        with col3:
            st.selectbox("NFPA Code", [""] + [f"{k} - {v}" for k, v in nfpa_codes.items()],
                         key=f"nfpa_{section}_{i}")
            st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key=f"media_{section}_{i}")

# PDF Generation
if st.button("Generate PDF Report"):
    filename = "inspection_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Header with logo & site image
    if logo:
        logo_path = "temp_logo.jpg"
        with open(logo_path, "wb") as f:
            f.write(logo.read())
        story.append(RLImage(logo_path, width=100))
        os.remove(logo_path)

    if site_image:
        site_img_path = "temp_site.jpg"
        with open(site_img_path, "wb") as f:
            f.write(site_image.read())
        story.append(RLImage(site_img_path, width=100))
        os.remove(site_img_path)

    story.append(Spacer(1, 12))
    story.append(Paragraph("Fire Safety Inspection Report", styles["Title"]))
    story.append(Paragraph(f"Client: {client_name}", styles["Normal"]))
    story.append(Paragraph(f"Location: {location}", styles["Normal"]))
    story.append(Paragraph(f"Date: {inspection_date}", styles["Normal"]))
    story.append(Spacer(1, 20))

    for section, questions in checklist_data.items():
        story.append(Paragraph(section, styles["Heading2"]))
        for i, q in enumerate(questions):
            status = st.session_state.get(f"status_{section}_{i}", "")
            note = st.session_state.get(f"note_{section}_{i}", "")
            uae = st.session_state.get(f"uae_{section}_{i}", "")
            nfpa = st.session_state.get(f"nfpa_{section}_{i}", "")
            image = st.session_state.get(f"media_{section}_{i}")

            story.append(Paragraph(f"<b>{q}</b>", styles["Normal"]))
            story.append(Paragraph(f"Status: {status}", styles["Normal"]))
            story.append(Paragraph(f"Note: {note}", styles["Normal"]))
            if uae:
                story.append(Paragraph(f"📘 UAE Code: {uae}", styles["Normal"]))
            if nfpa:
                story.append(Paragraph(f"📙 NFPA Code: {nfpa}", styles["Normal"]))

            if image:
                img_path = f"temp_{q.replace(' ', '_')}.jpg"
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())
                story.append(RLImage(img_path, width=200))
                os.remove(img_path)

            story.append(Spacer(1, 10))

    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Inspector: <b>{inspector_name}</b>", styles["Normal"]))

    if signature_image:
        sig_path = "temp_signature.jpg"
        with open(sig_path, "wb") as f:
            f.write(signature_image.read())
        story.append(Paragraph("Signature:", styles["Normal"]))
        story.append(RLImage(sig_path, width=100))
        os.remove(sig_path)

    doc.build(story)

    with open(filename, "rb") as f:
        st.download_button("Download PDF Report", f, file_name=filename)
