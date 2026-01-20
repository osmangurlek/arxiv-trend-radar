"""
Trends Page - View top and fastest-growing entities
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.title("📈 Trend Analytics")
st.markdown("Explore top entities and fastest-growing trends in AI/ML research.")

st.divider()

# Filters
col1, col2 = st.columns(2)

with col1:
    entity_type = st.selectbox(
        "Entity Type",
        options=["method", "dataset", "task", "library"],
        index=0,
        help="Select the type of entity to analyze"
    )

with col2:
    # Default to last Monday
    today = datetime.now()
    last_monday = today - timedelta(days=today.weekday() + 7)
    
    week_start = st.date_input(
        "Week Start",
        value=last_monday,
        help="Start of the week to analyze"
    )

st.divider()

# Fetch trends data
try:
    response = requests.get(
        f"{API_URL}/trends/week",
        params={
            "week_start": week_start.isoformat(),
            "entity_type": entity_type
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        col1, col2 = st.columns(2)
        
        # Top Entities
        with col1:
            st.markdown("### 🏆 Top Entities")
            st.caption(f"Most mentioned {entity_type}s in papers")
            
            top_entities = data.get("top_entities", [])
            if top_entities:
                df_top = pd.DataFrame(top_entities)
                
                # Add rank column
                df_top.insert(0, 'rank', range(1, len(df_top) + 1))
                df_top['rank'] = df_top['rank'].apply(lambda x: f"#{x}")
                
                # Style the dataframe
                st.dataframe(
                    df_top,
                    column_config={
                        "rank": st.column_config.TextColumn("Rank", width="small"),
                        "name": st.column_config.TextColumn("Entity", width="medium"),
                        "count": st.column_config.NumberColumn("Papers", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Simple bar chart
                st.bar_chart(df_top.set_index('name')['count'], color="#667eea")
            else:
                st.info(f"No {entity_type} entities found for this week.")
        
        # Fastest Growing
        with col2:
            st.markdown("### 🚀 Fastest Growing")
            st.caption("Week-over-week growth comparison")
            
            growing = data.get("fastest_growing", [])
            if growing:
                df_growing = pd.DataFrame(growing)
                
                # Add trend indicators
                df_growing['trend'] = df_growing['growth'].apply(
                    lambda x: "🔥" if x > 5 else ("📈" if x > 0 else "📉")
                )
                
                st.dataframe(
                    df_growing,
                    column_config={
                        "name": st.column_config.TextColumn("Entity", width="medium"),
                        "growth": st.column_config.NumberColumn("Growth", format="+%d"),
                        "trend": st.column_config.TextColumn("", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Growth chart
                st.bar_chart(df_growing.set_index('name')['growth'], color="#10b981")
            else:
                st.info("No growth data available. Need at least 2 weeks of data.")
    else:
        st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")
        
except requests.exceptions.ConnectionError:
    st.error("❌ Could not connect to the API. Make sure FastAPI is running.")
except Exception as e:
    st.error(f"Error: {str(e)}")

st.divider()

# Co-occurrence section
st.markdown("### 🔗 Entity Co-occurrence")
st.caption("Entities that frequently appear together in papers")

col1, col2 = st.columns([1, 3])

with col1:
    cooc_type = st.selectbox(
        "Co-occurrence Type",
        options=["method", "dataset", "task", "library"],
        key="cooc_type"
    )
    cooc_days = st.slider("Days", 7, 90, 30)

with col2:
    try:
        response = requests.get(
            f"{API_URL}/trends/cooccurrence",
            params={"entity_type": cooc_type, "days": cooc_days},
            timeout=30
        )
        
        if response.status_code == 200:
            cooc_data = response.json()
            
            if cooc_data:
                df_cooc = pd.DataFrame(cooc_data)
                
                st.dataframe(
                    df_cooc,
                    column_config={
                        "entity_a": st.column_config.TextColumn("Entity A"),
                        "entity_b": st.column_config.TextColumn("Entity B"),
                        "cooccurrence_count": st.column_config.NumberColumn("Co-occurrences", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No co-occurrence data available.")
    except requests.exceptions.ConnectionError:
        st.info("Connect to API to see co-occurrence data")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Sidebar info
with st.sidebar:
    st.markdown("### 📊 About Trends")
    st.markdown("""
    **Top Entities** shows the most frequently mentioned entities in papers for the selected week.
    
    **Fastest Growing** compares the current week to the previous week to find emerging trends.
    
    **Co-occurrence** shows which entities appear together in the same papers, revealing research patterns.
    """)
    
    st.divider()
    
    st.markdown("### 🔍 Entity Types")
    st.markdown("""
    - **Method**: Algorithms, architectures (e.g., Transformer, RAG)
    - **Dataset**: Named datasets (e.g., ImageNet, MS MARCO)
    - **Task**: Research problems (e.g., QA, Classification)
    - **Library**: Tools/frameworks (e.g., PyTorch, LangChain)
    """)

