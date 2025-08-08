import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os
import qrcode
from io import BytesIO
import smtplib
from email.message import EmailMessage

# ========== Dropdown Codes ==========
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

# ========== Static Inspection Checklist ==========
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
    # ✅ Add other sections here as needed
}

# ========== UI ==========
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
            st.radio("Status", ["Yes", "No", "N/A"], key=f"status_{section}_{i}", horizontal=True)
        with col2:
            st.text_area("Observations / Notes", height=150, key=f"note_{section}_{i}")
        with col3:
            st.selectbox("UAE Code", uae_fire_codes, key=f"uae_{section}_{i}")
        with col4:
            st.selectbox("NFPA Code", nfpa_codes, key=f"nfpa_{section}_{i}")
        with col5:
            st.file_uploader("Media", type=["jpg", "jpeg", "png"], key=f"media_{section}_{i}")

inspector_name = st.text_input("Inspector Name")
signature_image = st.file_uploader("Upload Signature", type=["jpg", "jpeg", "png"], key="signature")
email_to = st.text_input("Email the report to")

filename = "inspection_report.pdf"

# ========== PDF Generation ==========
def generate_pdf():
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Images
    if company_logo:
        with open("temp_logo.jpg", "wb") as f:
            f.write(company_logo.getbuffer())
        story.append(RLImage("temp_logo.jpg", width=100))
    if site_image:
        with open("temp_site.jpg", "wb") as f:
            f.write(site_image.getbuffer())
        story.append(RLImage("temp_site.jpg", width=100))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Fire Safety Inspection Report", styles["Title"]))
    story.append(Paragraph(f"Client Name: {client_name}", styles["Normal"]))
    story.append(Paragraph(f"Location: {location}", styles["Normal"]))
    story.append(Paragraph(f"Inspection Date: {inspection_date}", styles["Normal"]))
    story.append(Spacer(1, 20))

    for section, questions in checklist_data.items():
        story.append(Paragraph(section, styles["Heading2"]))
        for i, q in enumerate(questions):
            story.append(Paragraph(f"<b>{q}</b>", styles["Normal"]))
            story.append(Paragraph(f"Status: {st.session_state.get(f'status_{section}_{i}', '')}", styles["Normal"]))
            story.append(Paragraph(f"Note: {st.session_state.get(f'note_{section}_{i}', '')}", styles["Normal"]))
            story.append(Paragraph(f"UAE Code: {st.session_state.get(f'uae_{section}_{i}', '')}", styles["Normal"]))
            story.append(Paragraph(f"NFPA Code: {st.session_state.get(f'nfpa_{section}_{i}', '')}", styles["Normal"]))
            img = st.session_state.get(f"media_{section}_{i}")
            if img:
                img_path = f"temp_{section}_{i}.jpg"
                with open(img_path, "wb") as f:
                    f.write(img.getbuffer())
                story.append(RLImage(img_path, width=150))
                os.remove(img_path)
            story.append(Spacer(1, 10))

    story.append(Paragraph(f"Inspector Name: {inspector_name}", styles["Normal"]))
    if signature_image:
        with open("temp_sig.jpg", "wb") as f:
            f.write(signature_image.getbuffer())
        story.append(RLImage("temp_sig.jpg", width=100))
        os.remove("temp_sig.jpg")

    # QR Code
    qr = qrcode.make("https://your-download-link.com/report")
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    with open("qr_temp.jpg", "wb") as f:
        f.write(buf.read())
    story.append(Paragraph("QR Code to download report:", styles["Normal"]))
    story.append(RLImage("qr_temp.jpg", width=100))
    os.remove("qr_temp.jpg")

    doc.build(story)
    return filename

# ========== Email ==========
def send_email():
    if not email_to:
        st.warning("Please enter an email address.")
        return
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Fire Safety Inspection Report'
        msg['From'] = 'youremail@example.com'
        msg['To'] = email_to
        msg.set_content('Please find the attached inspection report.')
        with open(filename, "rb") as f:
            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=filename)
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('youremail@example.com', 'yourpassword')
            smtp.send_message(msg)
        st.success("✅ Email sent successfully.")
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")

# ========== Buttons ==========
if st.button("PDF Report"):
    generate_pdf()
    st.success("✅ PDF generated.")

    # Show download after generation
    with open(filename, "rb") as f:
        st.download_button("Download Report", f, file_name=filename)

if st.button("Send Email"):
    generate_pdf()
    send_email()




