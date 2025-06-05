import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import tempfile
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

st.set_page_config(page_title="Medicine Order Portal", layout="centered")
st.title("💊 Online Medicine Order")

# --- Form UI ---
with st.form("order_form"):
    st.subheader("📄 Patient & Prescription Info")
    patient_name = st.text_input("Patient's Name *")
    age = st.number_input("Age *", min_value=0, max_value=120, step=1)
    gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
    address = st.text_area("Delivery Address *")
    doctor_name = st.text_input("Prescribing Doctor's Name *")
    date_of_prescription = st.date_input("Date of Prescription", value=datetime.today())
    email = st.text_input("Your Email Address *")

    uploaded_file = st.file_uploader("📎 Upload Prescription (optional)", type=["pdf", "png", "jpg", "jpeg"])

    st.markdown("### ➕ Manually Enter Medicines (optional if uploading prescription)")
    medicines = []
    for i in range(1, 6):
        med_name = st.text_input(f"Medicine {i} Name", key=f"med_{i}")
        med_qty = st.number_input(f"Quantity", min_value=0, max_value=50, key=f"qty_{i}")
        if med_name and med_qty > 0:
            medicines.append({"Medicine": med_name, "Quantity": med_qty})

    submitted = st.form_submit_button("🛒 Place Order")

# --- PDF Generator ---
def generate_pdf(name, age, gender, doctor, date, address, meds, file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Medicine Order Receipt", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Patient: {name}, Age: {age}, Gender: {gender}", ln=True)
    pdf.cell(200, 10, txt=f"Doctor: {doctor}, Date: {date}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Address: {address}")
    pdf.ln(5)

    if meds:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Medicines:", ln=True)
        pdf.set_font("Arial", size=11)
        for m in meds:
            pdf.cell(0, 10, f"- {m['Medicine']} x {m['Quantity']}", ln=True)

    if file:
        pdf.ln(5)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "Prescription uploaded separately.", ln=True)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name

# --- Email Sender (Simulated for demo) ---
def send_email(recipient_email, subject, body, attachment_path):
    sender_email = "your_email@example.com"      # Replace with actual
    sender_password = "your_app_password"        # Replace with actual or use App Password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as file:
        part = MIMEApplication(file.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Email failed: {e}")
        return False

# --- Payment Mock UI ---
def show_payment_mock():
    st.markdown("## 💳 Proceed to Payment")
    st.info("This is a simulated payment screen (Razorpay/Stripe mock).")
    st.write("Amount to pay: ₹149.00")
    paid = st.button("✅ Simulate Payment Success")
    return paid

# --- On Form Submit ---
if submitted:
    if not (patient_name and age and gender and address and doctor_name and email):
        st.warning("Please fill all required fields.")
    elif not medicines and not uploaded_file:
        st.warning("Please either upload a prescription or enter medicine details.")
    else:
        st.success("✅ Order Details Saved! Proceed to Payment.")
        if show_payment_mock():  # Simulated payment step
            st.success("💸 Payment Successful!")

            pdf_path = generate_pdf(
                patient_name, age, gender, doctor_name,
                date_of_prescription.strftime("%Y-%m-%d"),
                address, medicines, uploaded_file
            )

            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download Your Order PDF", f, file_name="medicine_order.pdf")

            if st.button("✉️ Email Receipt"):
                if send_email(email, "Your Medicine Order Receipt", "Please find your receipt attached.", pdf_path):
                    st.success("📧 Email sent successfully to your inbox.")
