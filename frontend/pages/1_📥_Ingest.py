"""
Ingest Page - Fetch papers from arXiv
"""
import streamlit as st
import requests
import json


def _safe_json(response):
    """Parse JSON response safely; return None or dict. Avoids 'Expecting value: line 1 column 1' on empty/non-JSON."""
    if not response.text or not response.text.strip():
        return None
    try:
        return response.json()
    except json.JSONDecodeError:
        return None


st.set_page_config(page_title="Ingest Papers", page_icon="📥", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .success-box {
        background: linear-gradient(145deg, #065f46, #047857);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(145deg, #1e3a5f, #2563eb);
        color: white;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.title("📥 Ingest Papers")
st.markdown("Fetch papers from arXiv and extract entities using LLM.")

st.divider()

# Ingest Form
with st.form("ingest_form"):
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="e.g., retrieval augmented generation",
            help="Enter keywords to search for on arXiv"
        )
    
    with col2:
        days = st.number_input(
            "Days Back",
            min_value=1,
            max_value=365,
            value=7,
            help="Number of days to look back (not yet implemented in arXiv API)"
        )
    
    with col3:
        limit = st.number_input(
            "Max Papers",
            min_value=1,
            max_value=200,
            value=10,
            help="Maximum number of papers to fetch"
        )
    
    submitted = st.form_submit_button("🚀 Start Ingestion", use_container_width=True)

if submitted:
    if not query:
        st.error("❌ Please enter a search query")
    else:
        with st.spinner(f"Fetching papers for '{query}'... This may take a while due to LLM processing."):
            try:
                response = requests.post(
                    f"{API_URL}/ingest",
                    params={"query": query, "days": days, "limit": limit},
                    timeout=300  # 5 minutes timeout for LLM processing
                )
                
                if response.status_code == 200:
                    result = _safe_json(response)
                    if result is None:
                        st.error("❌ Invalid response from server.")
                    else:
                        st.success(f"✅ {result['message']}")
                        
                        st.markdown("### 📊 Ingestion Results")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Query", result.get("query", query))
                        with col2:
                            st.metric("Papers Added", result.get("papers_added", 0))
                        with col3:
                            st.metric("Status", "Success ✓")
                        
                        # Show ingested papers as messages
                        papers = result.get("papers") or []
                        if papers:
                            st.markdown("### 📄 Ingested Papers")
                            for p in papers:
                                title = (p.get("title") or "")[:100]
                                arxiv_id = p.get("arxiv_id", "")
                                pub = (p.get("published_at") or "")[:10]
                                st.info(f"📄 **{title}**{'…' if len(p.get('title','')) > 100 else ''}  \n`{arxiv_id}` · Published {pub}")
                        st.success("💡 Visit the **Trends** page to see the extracted entities!")
                else:
                    err_detail = _safe_json(response)
                    st.error(f"❌ Error: {(err_detail or {}).get('detail', response.text or 'Unknown error')}")
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. The ingestion might still be running on the server.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the API. Make sure FastAPI is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()

# Recent Papers Section
st.markdown("### 📄 Recent Papers")

try:
    response = requests.get(f"{API_URL}/papers/", params={"limit": 10}, timeout=10)
    
    if response.status_code == 200:
        papers = response.json()
        
        if papers:
            from collections import OrderedDict
            from datetime import datetime as _dt

            groups: OrderedDict = OrderedDict()
            for paper in papers:
                # Group by ingest date-time (minute precision)
                raw = paper.get("created_at") or ""
                try:
                    dt = _dt.fromisoformat(raw.replace("Z", "+00:00"))
                    group_key = dt.strftime("%b %d, %Y  %H:%M")
                except Exception:
                    group_key = raw[:16] if raw else "Unknown"
                groups.setdefault(group_key, []).append(paper)

            for group_label, group_papers in groups.items():
                st.markdown(f"**📅 Ingested: {group_label}** — {len(group_papers)} paper{'s' if len(group_papers) != 1 else ''}")
                for paper in group_papers:
                    title_short = paper['title'][:90] + ('…' if len(paper['title']) > 90 else '')
                    with st.expander(f"📄 {title_short}", expanded=False):
                        st.markdown(f"**ArXiv ID:** `{paper['arxiv_id']}`")
                        st.markdown(f"**Authors:** {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
                        st.markdown(f"**Published:** {paper['published_at'][:10]}")
                        st.markdown(f"**Categories:** {', '.join(paper['categories'])}")
                        st.markdown("**Abstract:**")
                        st.caption(paper['abstract'][:500] + "..." if len(paper['abstract']) > 500 else paper['abstract'])
                        st.markdown(f"[View on arXiv]({paper['url']})")
                st.caption("")
        else:
            st.info("No papers found. Start by ingesting some papers above!")
    else:
        st.warning("Could not fetch papers from API.")
except requests.exceptions.ConnectionError:
    st.info("ℹ️ Start the FastAPI server to see recent papers")
except Exception as e:
    st.error(f"Error: {str(e)}")

# Help section
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.markdown("""
    **Good search queries:**
    - `retrieval augmented generation`
    - `large language models`
    - `reinforcement learning`
    - `vision transformer`
    - `diffusion models`
    
    **Processing time:**
    - Each paper requires 2 LLM calls
    - ~2-5 seconds per paper
    - Start with 5-10 papers first
    """)

