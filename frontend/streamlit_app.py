"""
ArXiv Trend Radar - Streamlit Dashboard
Main entry point for the Streamlit application.
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ArXiv Trend Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    .main-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
    }
    
    .sub-header {
        font-family: 'Space Grotesk', sans-serif;
        color: #6b7280;
        font-size: 1.2rem;
        margin-top: 0;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    }
    
    .feature-box {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">📡 ArXiv Trend Radar</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Track AI/ML research trends with LLM-powered analytics</p>', unsafe_allow_html=True)

st.divider()

# Welcome section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🎯 What is ArXiv Trend Radar?")
    st.markdown("""
    ArXiv Trend Radar is a research intelligence tool that helps you stay on top of 
    the latest trends in AI/ML research. It:
    
    - 📥 **Ingests papers** from arXiv based on your queries
    - 🤖 **Extracts entities** (methods, datasets, tasks, libraries) using LLM
    - 📊 **Analyzes trends** with SQL analytics
    - 📝 **Generates digests** for weekly summaries
    """)
    
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    Use the sidebar to navigate between pages:
    
    1. **📥 Ingest** - Fetch papers from arXiv
    2. **📈 Trends** - View top and growing entities
    3. **🔍 Entity Explorer** - Explore entities and related papers
    4. **📝 Digest** - Generate weekly trend reports
    """)

with col2:
    st.markdown("### ⚡ Quick Stats")
    
    # Try to fetch stats from API
    import requests
    import os
    
    API_URL = os.environ.get("API_URL", "http://localhost:8000")
    
    try:
        papers_resp = requests.get(f"{API_URL}/papers/", params={"limit": 1000}, timeout=5)
        entities_resp = requests.get(f"{API_URL}/entities/", timeout=5)
        
        if papers_resp.status_code == 200 and entities_resp.status_code == 200:
            papers = papers_resp.json()
            entities = entities_resp.json()
            
            st.metric("📄 Papers", len(papers))
            st.metric("🏷️ Entities", len(entities))
            
            # Count by entity type
            type_counts = {}
            for e in entities:
                t = e.get("type", "unknown")
                type_counts[t] = type_counts.get(t, 0) + 1
            
            for etype, count in sorted(type_counts.items()):
                st.caption(f"  • {etype}: {count}")
        else:
            st.warning("⚠️ Could not fetch stats")
    except requests.exceptions.RequestException:
        st.info("ℹ️ Start the FastAPI server to see stats")
        st.code("uvicorn backend.app.main:app --reload", language="bash")

st.divider()

# Footer
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem;">
    <p>Built with ❤️ using FastAPI, PostgreSQL, LangChain & Streamlit</p>
    <p style="font-size: 0.8rem;">Make sure the FastAPI backend is running at <code>http://localhost:8000</code></p>
</div>
""", unsafe_allow_html=True)

