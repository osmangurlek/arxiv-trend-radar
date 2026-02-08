import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.schemas import PaperClassificationSchema

TAXONOMY_PROMPT = """You are a research paper classifier. Classify the paper into one or more of these categories:
Categories:
- Retrieval/RAG: Papers about retrieval-augmented generation, search, information retrieval
- Agents/Tool Use: Papers about AI agents, tool use, function calling
- Evaluation/Benchmarks: Papers about evaluation methods, benchmarks, metrics
- Alignment/Safety: Papers about AI safety, alignment, RLHF
- Multimodal: Papers about vision-language models, audio, video
- Systems/Optimization: Papers about training efficiency, inference optimization
- Other: Papers that don't fit above categories
Rules:
- Return 1-3 most relevant tags
- Each tag must have confidence 0.0-1.0
- Only use tags from the list above
Abstract:
{abstract}
"""

class ClassificationService:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-5.2",
            temperature=0,
            max_tokens=300
        )
        self.structured_llm = self.llm.with_structured_output(PaperClassificationSchema)
        self.prompt = ChatPromptTemplate.from_template(TAXONOMY_PROMPT)

    async def classify_paper(self, abstract: str, max_retries: int = 3) -> PaperClassificationSchema:
        chain = self.prompt | self.structured_llm
        
        for attempt in range(max_retries):
            try:
                result = await chain.ainvoke({"abstract": abstract})
                return result
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = (attempt + 1) * 10
                    print(f"⏳ Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                else:
                    raise e
        
        raise Exception(f"Failed after {max_retries} retries due to rate limiting")