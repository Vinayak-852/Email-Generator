import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import time
from datetime import datetime

# Configure Gemini API
genai.configure(api_key="AIzaSyCLbMRxsGWpVQv6rwX1RR8G8lR_gsRdKjs")

# Initialize session state for storing text and summary
if "book_text" not in st.session_state:
    st.session_state.book_text = ""
if "generated_summary" not in st.session_state:
    st.session_state.generated_summary = ""

# Streamlit app layout
st.title("📚 Book Summary Generator")
st.write("Enter a book description or text, select your preferences, and generate a concise summary. Download it as a PDF or regenerate with new settings.")

# Instructions
st.header("Step 1: Input Book Text")
st.write("Paste the book description or text you want summarized below.")
book_text = st.text_area("Book Text", height=200, placeholder="Enter the book description or text here...")

# Save book text to session state if changed
if book_text:
    st.session_state.book_text = book_text

# Step 2: Select Preferences
st.header("Step 2: Customize Summary")
col1, col2 = st.columns(2)

with col1:
    genre = st.selectbox("Category/Genre", ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Biography", "History", "Self-Help"])
    year = st.selectbox("Publication Year", list(range(1900, 2026)), index=125)  # Default to 2025
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Chinese", "Other"])

with col2:
    tags = st.text_input("Tags/Keywords (comma-separated)", placeholder="e.g., adventure, romance, technology")
    format_option = st.radio("Summary Format", ["Paragraph", "Bullet Points"])
    tone = st.radio("Tone", ["Formal", "Casual", "Academic"])

# Step 3: Generate Summary
st.header("Step 3: Generate and Download")
if st.button("Generate Summary"):
    if not st.session_state.book_text:
        st.error("Please enter book text to generate a summary.")
    else:
        with st.spinner("Generating summary..."):
            # Construct prompt for Gemini API
            prompt = f"""
            Generate a concise book summary based on the following text: 
            '{st.session_state.book_text}'
            
            Preferences:
            - Genre: {genre}
            - Publication Year: {year}
            - Language: {language}
            - Tags/Keywords: {tags}
            - Format: {format_option}
            - Tone: {tone}
            
            Provide the summary in {format_option} format with a {tone} tone, tailored to the specified genre and tags.
            """
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                st.session_state.generated_summary = response.text
                st.success("Summary generated successfully!")
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")

# Display generated summary
if st.session_state.generated_summary:
    st.subheader("Generated Summary")
    st.write(st.session_state.generated_summary)
    
    # PDF Generation
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(st.session_state.generated_summary, styles["Normal"]), Spacer(1, 12)]
    doc.build(story)
    buffer.seek(0)
    
    # Download button
    st.download_button(
        label="Download Summary as PDF",
        data=buffer,
        file_name=f"book_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

# Step 4: Regenerate Option
if st.session_state.generated_summary:
    st.header("Step 4: Regenerate Summary")
    st.write("Change the format or tone above and click below to regenerate the summary without re-entering the text.")
    if st.button("Regenerate Summary"):
        if not st.session_state.book_text:
            st.error("No book text available to regenerate summary.")
        else:
            with st.spinner("Regenerating summary..."):
                prompt = f"""
                Generate a concise book summary based on the following text: 
                '{st.session_state.book_text}'
                
                Preferences:
                - Genre: {genre}
                - Publication Year: {year}
                - Language: {language}
                - Tags/Keywords: {tags}
                - Format: {format_option}
                - Tone: {tone}
                
                Provide the summary in {format_option} format with a {tone} tone, tailored to the specified genre and tags.
                """
                try:
                    model = genai.GenerativeModel("gemini-2.0-flash")
                    response = model.generate_content(prompt)
                    st.session_state.generated_summary = response.text
                    st.success("Summary regenerated successfully!")
                except Exception as e:
                    st.error(f"Error regenerating summary: {str(e)}")
