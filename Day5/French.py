import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
import google.generativeai as genai

# ---------------------------
# SET GEMINI API KEY DIRECTLY
# ---------------------------
GOOGLE_API_KEY = "AIzaSyCLbMRxsGWpVQv6rwX1RR8G8lR_gsRdKjs"  # Replace with your actual Gemini API key
genai.configure(api_key=GOOGLE_API_KEY)

# ---------------------------
# DEFINE LLM AND PROMPT CHAIN
# ---------------------------
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a translator that translates English sentences to French."),
    ("user", "{english_text}")
])

# Create the LangChain Runnable chain
chain: Runnable = prompt | llm

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="English to French Translator", layout="centered")
st.title("🌍 English to French Translator")

st.markdown("Enter an English sentence below and click **Translate** to get the French version.")

# Input box
english_text = st.text_input("Enter English sentence:", "")

# Translate button
if st.button("Translate"):
    if not english_text.strip():
        st.warning("Please enter a valid English sentence.")
    else:
        try:
            # Run the chain with input
            response = chain.invoke({"english_text": english_text})
            
            # Extract response text
            french_translation = response.content.strip()

            # Show result
            st.success("✅ Translated Successfully!")
            st.markdown(f"**French Translation:**\n\n> {french_translation}")

        except Exception as e:
            st.error(f"⚠️ Error occurred during translation: {e}")
