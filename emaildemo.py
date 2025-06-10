import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("AIzaSyCLbMRxsGWpVQv6rwX1RR8G8lR_gsRdKjs"))

# Title
st.title("📧 AI Email Generator using Gemini")

# Step 1: User Input
user_input = st.text_area("Enter the purpose or content of your email:", height=200)

# Step 2: Format and Tone Options
format_option = st.selectbox("Select Email Format:", ["Formal", "Informal", "Professional", "Friendly"])
tone_option = st.radio("Select Email Tone:", ["Polite", "Confident", "Assertive", "Empathetic"])

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# Function to generate email
def generate_email(content, format_style, tone):
    prompt = f"""Write an {format_style.lower()} email with a {tone.lower()} tone.
    Content/Context: {content}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# Session state to keep the original input and generated email
if "email_text" not in st.session_state:
    st.session_state.email_text = ""

# Generate Button
if st.button("Generate Email"):
    if user_input.strip():
        st.session_state.email_text = generate_email(user_input, format_option, tone_option)
    else:
        st.warning("Please enter the content for the email.")

# Regenerate Button
if st.button("Regenerate with New Format/Tone"):
    if user_input.strip():
        st.session_state.email_text = generate_email(user_input, format_option, tone_option)
    else:
        st.warning("Please enter the content for the email.")

# Display the generated email
if st.session_state.email_text:
    st.subheader("✉️ Generated Email")
    st.text_area("Generated Email", st.session_state.email_text, height=300)

    # PDF Download
    def create_pdf(text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)
        return pdf

    pdf = create_pdf(st.session_state.email_text)
    pdf_output = "generated_email.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as file:
        st.download_button(
            label="📄 Download as PDF",
            data=file,
            file_name="generated_email.pdf",
            mime="application/pdf"
        )
