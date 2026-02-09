import streamlit as st

st.set_page_config(
    page_title="Career Coach Nautilos",
    page_icon="🧭",
    layout="wide"
)

st.title("🧭 Career Coach Nautilos")

st.markdown("""
## Welcome to Nautilos - Your AI Career Navigator

Choose a tool from the sidebar:

### 📊 Job Match Analysis
Analyze how well your resume matches a job description. Get skill gap analysis and recommendations.

### ✍️ Resume Tailor
Generate a tailored resume optimized for a specific job description using your accomplishments bank.

---

**Get started by selecting a page from the sidebar →**
""")

st.info("💡 Tip: Upload your resume once, then use it across both tools!")