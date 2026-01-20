from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.schemas import CanonicalizationSchema
from typing import List

CANONICALIZATION_PROMPT = """You are an entity deduplication expert. Given a list of entity names, 
identify which ones refer to the same concept and group them.
For each group:
- "canonical" should be the most complete, formal name
- "aliases" should be shorter forms, abbreviations, or variations
Examples:
- canonical: "Reinforcement Learning from Human Feedback", aliases: ["RLHF", "rlhf"]
- canonical: "Retrieval-Augmented Generation", aliases: ["RAG", "retrieval augmented generation"]
- canonical: "Large Language Model", aliases: ["LLM", "LLMs"]
Rules:
- Only group entities that truly refer to the same concept
- If an entity has no aliases, don't include it
- Be conservative - when in doubt, don't merge
Entity names:
{entity_names}
"""

class CanonicalizationService:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-5.2",
            temperature=0,
            max_tokens=2000
        )
        self.structured_llm = self.llm.with_structured_output(CanonicalizationSchema)
        self.prompt = ChatPromptTemplate.from_template(CANONICALIZATION_PROMPT)

    async def find_canonical_groups(self, entity_names: List[str]) -> CanonicalizationSchema:
        chain = self.prompt | self.structured_llm
        result = await chain.ainvoke({"entity_names": entity_names})
        return result