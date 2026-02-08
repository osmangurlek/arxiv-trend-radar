import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import date

DIGEST_PROMPT = """You are a research trends analyst. Generate a weekly digest based on the following data.
## This Week's Data
### Top Entities (by paper count):
{top_entities}
### Fastest Growing Entities:
{fastest_growing}
### Entity Co-occurrence (what's used together):
{cooccurrence}
### Category Distribution:
{categories}
---
Generate a markdown digest with these sections:
# Weekly ArXiv Trends Digest
**Week of {week_start}**
## 🔥 Key Trends
- List top 3-5 trends with brief explanations
## 📈 Rising Topics
- List 2-3 fastest growing topics and why they might be gaining traction
## 🔗 Interesting Connections
- List 2-3 entity co-occurrences that reveal emerging research patterns
## 📚 Recommended Reading Areas
- Suggest 3-5 areas to explore based on the data
Keep it concise and actionable for ML researchers.
"""

class DigestService:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-5.2",
            temperature=0.3,
            max_tokens=1200
        )
        self.prompt = ChatPromptTemplate.from_template(DIGEST_PROMPT)
    
    async def generate_digest(
        self,
        week_start: date,
        top_entities: list,
        fastest_growing: list,
        cooccurrence: list,
        categories: list,
        max_retries: int = 3
    ) -> str:
        """Generate weekly digest markdown"""
        chain = self.prompt | self.llm
        
        # Format data for prompt
        top_str = "\n".join([f"- {e['name']}: {e['count']} papers" for e in top_entities]) or "No data"
        growth_str = "\n".join([f"- {e['name']}: +{e['growth']}" for e in fastest_growing]) or "No data"
        cooc_str = "\n".join([f"- {e['entity_a']} + {e['entity_b']}: {e['count']} papers" for e in cooccurrence]) or "No data"
        cat_str = "\n".join([f"- {c['category']}: {c['count']}" for c in categories[:10]]) or "No data"
        
        for attempt in range(max_retries):
            try:
                result = await chain.ainvoke({
                    "week_start": week_start.isoformat(),
                    "top_entities": top_str,
                    "fastest_growing": growth_str,
                    "cooccurrence": cooc_str,
                    "categories": cat_str
                })
                # Handle both string and list content formats from LLM
                content = result.content
                if isinstance(content, list):
                    # Extract text from list format: [{'type': 'text', 'text': '...'}]
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    content = ''.join(text_parts)
                return content
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = (attempt + 1) * 10
                    print(f"⏳ Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
        
        raise Exception(f"Failed after {max_retries} retries due to rate limiting")