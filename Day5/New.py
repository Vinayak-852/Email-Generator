import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory

import tempfile
import os

# --- Set API KEY ---
GOOGLE_API_KEY = "AIzaSyCLbMRxsGWpVQv6rwX1RR8G8lR_gsRdKjs"  # Replace with your Gemini API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# --- Initialize memory ---
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ConversationBufferMemory(return_messages=True)

# --- Streamlit UI ---
st.set_page_config(page_title="RAG with Gemini", layout="centered")
st.title("📄 Gemini RAG App (PDF + Prompt)")
st.markdown("Upload a PDF and ask a question about its contents.")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
user_input = st.text_input("Enter your question (English):", "")
submit_btn = st.button("Get Answer")

if submit_btn:
    if not uploaded_file:
        st.warning("Please upload a PDF.")
    elif not user_input.strip():
        st.warning("Please enter a valid question.")
    else:
        try:
            # Step 1: Load PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                pdf_path = tmp_file.name

            loader = PyPDFLoader(pdf_path)
            documents = loader.load()

            # Step 2: Chunk text
            splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(documents)

            # Step 3: Embedding + Vector DB
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectorstore = FAISS.from_documents(chunks, embeddings)

            # Step 4: Retrieve top chunks
            retriever = vectorstore.as_retriever(search_type="similarity", k=4)
            retrieved_docs = retriever.invoke(user_input)

            context = "\n\n".join([doc.page_content for doc in retrieved_docs])

            # Step 5: Prompt Template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant. Use the following context and chat history to answer the question."),
                ("human", "Context:\n{context}\n\nChat History:\n{chat_history}\n\nQuestion: {question}")
            ])

            # Step 6: Gemini LLM
            llm = ChatGoogleGenerativeAI(
                model="models/gemini-1.5-flash-latest",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.2
            )

            # Step 7: Prepare memory and chain
            memory = st.session_state.chat_memory
            chat_history = memory.buffer_as_messages

            chain = prompt | llm

            # Step 8: Invoke chain with memory
            result = chain.invoke({
                "context": context,
                "question": user_input,
                "chat_history": chat_history
            })

            # Save to memory
            memory.chat_memory.add_user_message(user_input)
            memory.chat_memory.add_ai_message(result.content)

            # Step 9: Display output
            st.success("✅ Response generated!")
            st.markdown("### 💬 Answer:")
            st.write(result.content)

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
