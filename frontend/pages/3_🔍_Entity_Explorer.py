"""
Entity Explorer Page - Browse entities and their related papers
"""
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Entity Explorer", page_icon="🔍", layout="wide")

import os
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.title("🔍 Entity Explorer")
st.markdown("Explore entities and discover related papers.")

st.divider()

# Filters
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    entity_type = st.selectbox(
        "Entity Type",
        options=["All", "method", "dataset", "task", "library"],
        index=0
    )

with col2:
    search_term = st.text_input(
        "Search",
        placeholder="Filter by name...",
        help="Search entities by name"
    )

# Fetch entities
try:
    params = {}
    if entity_type != "All":
        params["entity_type"] = entity_type
    if search_term:
        params["search"] = search_term
    
    response = requests.get(f"{API_URL}/entities/", params=params, timeout=30)
    
    if response.status_code == 200:
        entities = response.json()
        
        with col3:
            st.metric("Total Entities", len(entities))
        
        st.divider()
        
        if entities:
            # Entity selection
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### 📋 Entities")
                
                # Group by type for better organization
                df = pd.DataFrame(entities)
                
                # Create a display name with type badge
                df['display'] = df.apply(
                    lambda x: f"{x['name']} [{x['type']}]", axis=1
                )
                
                # Entity selector
                selected_entity = st.selectbox(
                    "Select an entity",
                    options=entities,
                    format_func=lambda x: f"{x['name']} ({x['type']})",
                    help="Select an entity to see related papers"
                )
                
                if selected_entity:
                    st.markdown("#### Entity Details")
                    st.markdown(f"**Name:** {selected_entity['name']}")
                    st.markdown(f"**Type:** `{selected_entity['type']}`")
                    st.markdown(f"**ID:** {selected_entity['id']}")
                    
                    if selected_entity.get('canonical_id'):
                        st.markdown(f"**Canonical ID:** {selected_entity['canonical_id']}")
                        st.caption("This entity is an alias")
                
                # Entity type breakdown
                st.markdown("#### Type Distribution")
                type_counts = df['type'].value_counts()
                for t, c in type_counts.items():
                    emoji = {"method": "🔧", "dataset": "📊", "task": "🎯", "library": "📚"}.get(t, "📌")
                    st.caption(f"{emoji} {t}: {c}")
            
            with col2:
                st.markdown("### 📄 Related Papers")
                
                if selected_entity:
                    try:
                        papers_resp = requests.get(
                            f"{API_URL}/entities/{selected_entity['id']}/papers",
                            timeout=30
                        )
                        
                        if papers_resp.status_code == 200:
                            papers = papers_resp.json()
                            
                            if papers:
                                st.caption(f"Found {len(papers)} papers mentioning **{selected_entity['name']}**")
                                
                                for paper in papers:
                                    with st.expander(f"📄 {paper['title'][:70]}...", expanded=False):
                                        st.markdown(f"**Authors:** {', '.join(paper['authors'][:3])}...")
                                        st.markdown(f"**Published:** {paper['published_at'][:10]}")
                                        
                                        # Evidence and confidence
                                        if paper.get('evidence'):
                                            st.markdown("**Evidence from abstract:**")
                                            st.info(f'"{paper["evidence"]}"')
                                        
                                        if paper.get('confidence'):
                                            confidence_pct = int(paper['confidence'] * 100)
                                            st.progress(paper['confidence'], text=f"Confidence: {confidence_pct}%")
                            else:
                                st.info("No papers found for this entity.")
                        else:
                            st.warning("Could not fetch papers for this entity.")
                    except Exception as e:
                        st.error(f"Error fetching papers: {e}")
                else:
                    st.info("👈 Select an entity from the left to see related papers")
        else:
            st.info("No entities found. Try adjusting your filters or ingest some papers first!")
    else:
        st.error(f"API Error: {response.json().get('detail', 'Unknown error')}")

except requests.exceptions.ConnectionError:
    st.error("❌ Could not connect to the API. Make sure FastAPI is running.")
    st.code("uvicorn backend.app.main:app --reload", language="bash")
except Exception as e:
    st.error(f"Error: {str(e)}")

# Co-occurrence neighbors section
st.divider()
st.markdown("### 🔗 Co-occurrence Network")
st.caption("See which entities frequently appear together")

if 'selected_entity' in dir() and selected_entity:
    try:
        cooc_resp = requests.get(
            f"{API_URL}/trends/cooccurrence",
            params={"entity_type": selected_entity['type'], "days": 30},
            timeout=30
        )
        
        if cooc_resp.status_code == 200:
            cooc_data = cooc_resp.json()
            
            # Filter to show only neighbors of selected entity
            neighbors = []
            for edge in cooc_data:
                if edge['entity_a'] == selected_entity['name']:
                    neighbors.append({
                        "neighbor": edge['entity_b'],
                        "co_occurrences": edge['cooccurrence_count']
                    })
                elif edge['entity_b'] == selected_entity['name']:
                    neighbors.append({
                        "neighbor": edge['entity_a'],
                        "co_occurrences": edge['cooccurrence_count']
                    })
            
            if neighbors:
                st.markdown(f"**Entities that co-occur with {selected_entity['name']}:**")
                df_neighbors = pd.DataFrame(neighbors).drop_duplicates()
                df_neighbors = df_neighbors.sort_values('co_occurrences', ascending=False)
                
                st.dataframe(
                    df_neighbors,
                    column_config={
                        "neighbor": st.column_config.TextColumn("Entity"),
                        "co_occurrences": st.column_config.NumberColumn("Co-occurrences", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(f"No co-occurrence data found for {selected_entity['name']}")
    except Exception as e:
        st.caption(f"Could not load co-occurrence data: {e}")

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 About Explorer")
    st.markdown("""
    The Entity Explorer lets you:
    
    1. **Browse entities** extracted from papers
    2. **Search** by name or filter by type
    3. **View papers** that mention an entity
    4. **See evidence** - the exact text where the entity was found
    5. **Explore connections** between entities
    """)
    
    st.divider()
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Click on a paper to see details
    - The **evidence** shows where the entity was found in the abstract
    - **Confidence** indicates how certain the LLM was about the extraction
    """)

