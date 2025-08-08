# Updated full Streamlit app with:
# - Company logo top left
# - Site image top right
# - Email the report to (input + button)
# - Download PDF report button
# - Dropdowns for UAE and NFPA codes
# - Inspector name + signature

import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO
import os
import qrcode
import smtplib
from email.message import EmailMessage

# Sample Fire Codes
uae_codes = {
    "UAE-C1": "Control panels must be clearly labeled",
    "UAE-C2": "Battery backup required for all systems"
}
nfpa_codes = {
    "NFPA-72": "National Fire Alarm Code",
    "NFPA-101": "Life Safety Code"
}

checklist_data = {
    "FIRE DETECTION & ALARM SYSTEM (FDAS)": [
        "Main Panel – Working / Not working",
        "Batteries Available – Yes / No"
    ],
    "EMERGENCY & EXIT LIGHTS": [
        "Exit Lights Installed"
    ]
}

st.set_page_config(page_title="Fire Safety Inspection Report", layout="wide")

# --- Upload top logo & image ---
col_logo, col_img = st.columns([1, 1])
with col_logo:
    company_logo = st.file_uploader("Upload Company Logo", type=["jpg", "jpeg", "png"], key="logo")
with col_img:
    site_image = st.file_uploader("Upload Site Image", type=["jpg", "jpeg", "png"], key="site")

st.title("Fire Safety Inspection Report")

client_name = st.text_input("Client Name")
location = st.text_input("Location")
inspection_date = st.date_input("Inspection Date")

# Checklist Section
st.header("Inspection Checklist")
all_responses = []
for section, questions in checklist_data.items():
    st.subheader(section)
    for i, q in enumerate(questions):
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"**{q}**")
            status = st.radio("Status", ["Yes", "No", "N/A"], key=f"status_{section}_{i}", horizontal=True)
            note = st.text_area("Observation", key=f"note_{section}_{i}")
        with col2:
            uae = st.selectbox("UAE Code", options=["None"] + list(uae_codes.keys()), key=f"uae_{section}_{i}")
            nfpa = st.selectbox("NFPA Code", options=["None"] + list(nfpa_codes.keys()), key=f"nfpa_{section}_{i}")
        with col3:
            image = st.file_uploader("Attach Media", type=["jpg", "jpeg", "png"], key=f"media_{section}_{i}")
        all_responses.append((section, q, status, note, uae, nfpa, image))

inspector_name = st.text_input("Inspector Name")
signature_image = st.file_uploader("Upload Signature", type=["jpg", "jpeg", "png"], key="signature")

# --- Email and Buttons ---
st.header("Finalize")
recipient_email = st.text_input("Email the report to")

def create_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Logo and site image
    if company_logo:
        logo_path = "temp_logo.jpg"
        with open(logo_path, "wb") as f: f.write(company_logo.getbuffer())
        story.append(RLImage(logo_path, width=100))
        os.remove(logo_path)
    if site_image:
        site_path = "temp_site.jpg"
        with open(site_path, "wb") as f: f.write(site_image.getbuffer())
        story.append(RLImage(site_path, width=120))
        os.remove(site_path)

    story.append(Paragraph("Fire Safety Inspection Report", styles["Title"]))
    story.append(Paragraph(f"Client Name: {client_name}", styles["Normal"]))
    story.append(Paragraph(f"Location: {location}", styles["Normal"]))
    story.append(Paragraph(f"Date: {inspection_date}", styles["Normal"]))
    story.append(Spacer(1, 20))

    for section, q, status, note, uae, nfpa, image in all_responses:
        story.append(Paragraph(f"<b>{q}</b>", styles["Normal"]))
        story.append(Paragraph(f"Status: {status}", styles["Normal"]))
        story.append(Paragraph(f"Note: {note}", styles["Normal"]))
        if uae != "None":
            story.append(Paragraph(f"UAE Code: {uae} - {uae_codes[uae]}", styles["Normal"]))
        if nfpa != "None":
            story.append(Paragraph(f"NFPA Code: {nfpa} - {nfpa_codes[nfpa]}", styles["Normal"]))
        if image:
            img_path = f"temp_img_{q[:10].replace(' ', '_')}.jpg"
            with open(img_path, "wb") as f: f.write(image.getbuffer())
            story.append(RLImage(img_path, width=200))
            os.remove(img_path)
        story.append(Spacer(1, 10))

    story.append(Paragraph(f"Inspector: {inspector_name}", styles["Normal"]))
    if signature_image:
        sig_path = "temp_sig.jpg"
        with open(sig_path, "wb") as f: f.write(signature_image.getbuffer())
        story.append(RLImage(sig_path, width=100))
        os.remove(sig_path)

    # Add QR code to download
    qr = qrcode.make("https://yourdomain.com/download/inspection.pdf")
    qr_path = "qr_code.png"
    qr.save(qr_path)
    story.append(Spacer(1, 15))
    story.append(Paragraph("Scan to download:", styles["Normal"]))
    story.append(RLImage(qr_path, width=100))
    os.remove(qr_path)

    doc.build(story)
    buffer.seek(0)
    return buffer

if st.button("PDF Report"):
    pdf_buffer = create_pdf()
    st.success("✅ PDF generated!")
    st.download_button("Download the Report", data=pdf_buffer, file_name="fire_safety_report.pdf", mime="application/pdf")

    # Optional: Send email (only works if SMTP configured)
    if recipient_email:
        msg = EmailMessage()
        msg['Subject'] = "Fire Inspection Report"
        msg['From'] = "your@email.com"
        msg['To'] = recipient_email
        msg.set_content("Attached is the fire safety inspection report.")
        msg.add_attachment(pdf_buffer.read(), maintype='application', subtype='pdf', filename="fire_safety_report.pdf")
        try:
            with smtplib.SMTP('smtp.yourhost.com', 587) as smtp:
                smtp.starttls()
                smtp.login("your@email.com", "yourpassword")
                smtp.send_message(msg)
                st.success("📩 Report sent to email!")
        except:
            st.warning("Email sending failed. Check SMTP settings.")


