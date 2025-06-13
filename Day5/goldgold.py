import streamlit as st
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI

# 🚨 Hardcoded API Key (for testing only — insecure for production)
GOOGLE_API_KEY = "AIzaSyCLbMRxsGWpVQv6rwX1RR8G8lR_gsRdKjs"

# 🌐 Initialize Gemini Model
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
except Exception as e:
    st.error("❌ Failed to initialize Gemini LLM. Check API key or model name.")
    st.stop()

# 🔎 Initialize DuckDuckGo Search tool (ensure dependency is installed)
try:
    search = DuckDuckGoSearchRun()
except ImportError as e:
    st.error("❌ DuckDuckGo tool requires the 'duckduckgo-search' package. Run:\n\n`pip install duckduckgo-search`")
    st.stop()

tools = [
    Tool(
        name="DuckDuckGo Search",
        func=search.run,
        description="Useful for answering real-time questions about current events or general knowledge."
    )
]

# 🤖 Initialize Agent
try:
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False
    )
except Exception as e:
    st.error(f"❌ Failed to initialize the agent.\n\n{e}")
    st.stop()

# 🎨 Streamlit UI
st.set_page_config(page_title="🌍 Ask Anything - Real Time QA", page_icon="🔍")
st.title("🔍 Ask Anything: Real-Time Q&A with Gemini + DuckDuckGo")

st.markdown("Type a question about **current events, facts, or news** and get instant answers using AI + live search. 🌐🧠")

user_question = st.text_input("💬 What's your question?", placeholder="e.g., Who won the IPL 2025 final?")

if st.button("🚀 Get Answer"):
    if user_question.strip() == "":
        st.warning("❗ Please enter a valid question.")
    else:
        with st.spinner("Thinking... 🤖"):
            try:
                response = agent.run(user_question)
                st.success("✅ Answer:")
                st.write(response)
            except Exception as e:
                st.error(f"⚠️ Oops! Something went wrong:\n\n{str(e)}")
