import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import qrcode
import base64
from io import BytesIO
import smtplib
from email.message import EmailMessage

# Sample UAE Fire Codes and NFPA Codes
uae_codes = {
    "UAE 501": "Fire Alarm System Requirements",
    "UAE 502": "Emergency Exit Lighting Standards",
    "UAE 503": "Fire Hose Reel Installation"
}
nfpa_codes = {
    "NFPA 72": "National Fire Alarm and Signaling Code",
    "NFPA 10": "Standard for Portable Fire Extinguishers",
    "NFPA 13": "Installation of Sprinkler Systems"
}

# Sample checklist
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
    ]
    # Add all remaining sections here from the PDF you referenced
}

st.set_page_config(page_title="Fire Safety Inspection Report", layout="wide")
st.title("Fire Safety Inspection Report")

client_name = st.text_input("Client Name")
location = st.text_input("Location")
inspection_date = st.date_input("Inspection Date")

col_logo, col_site = st.columns([1, 1])
with col_logo:
    logo = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"])
with col_site:
    site_img = st.file_uploader("Upload Site Image", type=["png", "jpg", "jpeg"])

st.header("Inspection Checklist")
for section, questions in checklist_data.items():
    st.subheader(section)
    for i, q in enumerate(questions):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            st.markdown(f"**{q}**")
            st.radio("Status", ["Yes", "No", "N/A"], key=f"status_{section}_{i}", horizontal=True)
        with col2:
            st.text_area("Observations / Notes", height=100, key=f"note_{section}_{i}")
        with col3:
            st.selectbox("UAE Code", list(uae_codes.keys()), key=f"uae_{section}_{i}")
            st.selectbox("NFPA Code", list(nfpa_codes.keys()), key=f"nfpa_{section}_{i}")
        with col4:
            st.file_uploader("Media", type=["jpg", "jpeg", "png"], key=f"media_{section}_{i}")

st.header("Inspector Details")
inspector_name = st.text_input("Inspector Name")
signature_image = st.file_uploader("Upload Signature", type=["png", "jpg", "jpeg"])
receiver_email = st.text_input("Recipient Email")

if st.button("PDF Report"):
    filename = "inspection_report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    if logo or site_img:
        logo_path = site_path = None
        img_row = []

        if logo:
            logo_path = "temp_logo.jpg"
            with open(logo_path, "wb") as f:
                f.write(logo.read())
            img_row.append(RLImage(logo_path, width=2*inch))
        else:
            img_row.append(Spacer(1, 2*inch))

        if site_img:
            site_path = "temp_site.jpg"
            with open(site_path, "wb") as f:
                f.write(site_img.read())
            img_row.append(RLImage(site_path, width=2*inch))
        else:
            img_row.append(Spacer(1, 2*inch))

        story.append(Table([img_row], colWidths=[3*inch, 3*inch], hAlign='LEFT'))
        story.append(Spacer(1, 12))

    story.append(Paragraph("Fire Safety Inspection Report", styles["Title"]))
    story.append(Paragraph(f"Client Name: {client_name}", styles["Normal"]))
    story.append(Paragraph(f"Location: {location}", styles["Normal"]))
    story.append(Paragraph(f"Inspection Date: {inspection_date}", styles["Normal"]))
    story.append(Spacer(1, 20))

    for section, questions in checklist_data.items():
        story.append(Paragraph(f"{section}", styles["Heading2"]))
        for i, q in enumerate(questions):
            status = st.session_state.get(f"status_{section}_{i}", "")
            note = st.session_state.get(f"note_{section}_{i}", "")
            uae_code = st.session_state.get(f"uae_{section}_{i}", "")
            nfpa_code = st.session_state.get(f"nfpa_{section}_{i}", "")
            image = st.session_state.get(f"media_{section}_{i}", None)

            story.append(Paragraph(f"<b>{q}</b>", styles["Normal"]))
            story.append(Paragraph(f"Status: {status}", styles["Normal"]))
            story.append(Paragraph(f"Notes: {note}", styles["Normal"]))
            story.append(Paragraph(f"UAE Code: {uae_code} - {uae_codes.get(uae_code)}", styles["Normal"]))
            story.append(Paragraph(f"NFPA Code: {nfpa_code} - {nfpa_codes.get(nfpa_code)}", styles["Normal"]))

            if image:
                img_path = f"temp_{section}_{i}.jpg"
                with open(img_path, "wb") as f:
                    f.write(image.read())
                story.append(RLImage(img_path, width=2*inch))
                os.remove(img_path)
            story.append(Spacer(1, 10))

    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Inspector Name: <b>{inspector_name}</b>", styles["Normal"]))
    if signature_image:
        sig_path = "temp_sig.jpg"
        with open(sig_path, "wb") as f:
            f.write(signature_image.read())
        story.append(RLImage(sig_path, width=100))
        os.remove(sig_path)

    # Add QR Code
    qr = qrcode.make("https://your-download-link.com")
    qr_path = "qr_code.png"
    qr.save(qr_path)
    story.append(Spacer(1, 12))
    story.append(Paragraph("Scan to download this report:", styles["Normal"]))
    story.append(RLImage(qr_path, width=100))
    os.remove(qr_path)

    doc.build(story)

    with open(filename, "rb") as f:
        st.download_button("Download PDF Report", f, file_name=filename)

    if receiver_email:
        msg = EmailMessage()
        msg['Subject'] = 'Fire Safety Inspection Report'
        msg['From'] = "you@example.com"
        msg['To'] = receiver_email
        msg.set_content("Please find the attached Fire Safety Inspection Report.")

        with open(filename, "rb") as f:
            report_data = f.read()
        msg.add_attachment(report_data, maintype='application', subtype='pdf', filename=filename)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("your_email@gmail.com", "your_password")
                smtp.send_message(msg)
                st.success("Report sent to email successfully.")
        except Exception as e:
            st.error(f"Failed to send email: {e}")

