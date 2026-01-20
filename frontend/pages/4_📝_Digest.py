"""
Digest Page - Generate and view weekly digests
"""
import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Weekly Digest", page_icon="📝", layout="wide")

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.title("📝 Weekly Digest")
st.markdown("Generate LLM-powered weekly trend reports based on database analytics.")

st.divider()

# Two columns: Generate and Latest
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🔄 Generate New Digest")
    
    # Default to last Monday
    today = datetime.now()
    last_monday = today - timedelta(days=today.weekday() + 7)
    
    with st.form("digest_form"):
        week_start = st.date_input(
            "Week Start Date",
            value=last_monday,
            help="Select the Monday of the week you want to analyze"
        )
        
        st.caption(f"Week: {week_start} to {week_start + timedelta(days=7)}")
        
        generate_btn = st.form_submit_button("🚀 Generate Digest", use_container_width=True)
    
    if generate_btn:
        with st.spinner("Generating digest... This may take 30-60 seconds."):
            try:
                response = requests.post(
                    f"{API_URL}/digest/generate",
                    params={"week_start": week_start.isoformat()},
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Digest generated successfully!")
                    
                    # Store in session state to display
                    st.session_state['generated_digest'] = result.get('content', '')
                    st.session_state['digest_week'] = str(week_start)
                    st.rerun()
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"❌ Error: {error_detail}")
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. Try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to API. Make sure FastAPI is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    st.markdown("### ℹ️ What's in a Digest?")
    st.markdown("""
    The digest is generated using **real data from your database**:
    
    - 🏆 Top entities by paper count
    - 🚀 Fastest growing entities
    - 🔗 Entity co-occurrences
    - 📊 Category distribution
    
    The LLM synthesizes this data into an actionable report.
    """)

with col2:
    st.markdown("### 📄 Latest Digest")
    
    # Show generated digest if available in session state
    if 'generated_digest' in st.session_state and st.session_state['generated_digest']:
        st.info(f"📅 Week of {st.session_state.get('digest_week', 'Unknown')}")
        st.markdown(st.session_state['generated_digest'])
        
        # Download button
        st.download_button(
            label="📥 Download Markdown",
            data=st.session_state['generated_digest'],
            file_name=f"digest_{st.session_state.get('digest_week', 'unknown')}.md",
            mime="text/markdown"
        )
    else:
        # Try to fetch latest from API
        try:
            response = requests.get(f"{API_URL}/digest/latest", timeout=30)
            
            if response.status_code == 200:
                digest = response.json()
                
                st.info(f"📅 Week: {digest['week_start'][:10]} to {digest['week_end'][:10]}")
                st.markdown(digest['content'])
                
                # Download button
                st.download_button(
                    label="📥 Download Markdown",
                    data=digest['content'],
                    file_name=f"digest_{digest['week_start'][:10]}.md",
                    mime="text/markdown"
                )
            elif response.status_code == 404:
                st.info("No digests found. Generate your first one! 👈")
                
                # Show placeholder
                st.markdown("""
                ### 📝 Sample Digest Structure
                
                ```markdown
                # Weekly ArXiv Trends Digest
                **Week of 2026-01-06**
                
                ## 🔥 Key Trends
                - Trend 1: ...
                - Trend 2: ...
                
                ## 📈 Rising Topics
                - Topic 1: ...
                
                ## 🔗 Interesting Connections
                - Connection 1: ...
                
                ## 📚 Recommended Reading Areas
                - Area 1: ...
                ```
                """)
            else:
                st.warning("Could not fetch latest digest.")
        except requests.exceptions.ConnectionError:
            st.warning("Connect to API to see the latest digest.")
            st.info("Start the FastAPI server:")
            st.code("uvicorn backend.app.main:app --reload", language="bash")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Sidebar with history
with st.sidebar:
    st.markdown("### 📚 Digest History")
    st.caption("Previous digests are stored in the database.")
    
    st.markdown("""
    To view a specific week's digest, generate it using the form. 
    If it already exists, it will be regenerated with fresh analysis.
    """)
    
    st.divider()
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Generate digests after ingesting new papers
    - Best results with at least 20-30 papers
    - Digests work best when you have 2+ weeks of data (for growth analysis)
    """)

