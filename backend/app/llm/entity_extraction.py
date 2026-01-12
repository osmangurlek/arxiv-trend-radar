from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.schemas import PaperExtractionSchema

SYSTEM_PROMPT = """You are an academic entity extraction assistant specializing in AI/ML research papers.

Your task is to extract **specific, standardized technical entities** from paper abstracts.

## ENTITY TYPES:
- **tasks**: Research problems or applications (e.g., "Image Classification", "Object Detection", "White Balance", "Color Constancy")
- **datasets**: Named datasets used for training/evaluation (e.g., "ImageNet", "COCO", "MS MARCO")
- **methods**: Algorithms, architectures, or techniques (e.g., "Transformer", "CNN", "Reinforcement Learning", "Adam Optimizer")
- **libraries**: Software tools or frameworks (e.g., "PyTorch", "TensorFlow", "LangChain", "Hugging Face")

## EXTRACTION RULES:
1. Extract **canonical technical terms**, NOT long phrases or sentences
2. Use **Title Case** for entity names (e.g., "Deep Reinforcement Learning" not "deep reinforcement learning")
3. Extract **specific named entities** when available (e.g., "RL-AWB" as a method, not "a novel framework")
4. Keep entity names **concise** (1-4 words typically)
5. The "evidence" field must be a SHORT quote (5-15 words) from the abstract showing where you found this entity
6. Do NOT extract generic phrases like "novel approach" or "our method" - extract the actual technical name
7. If an acronym is defined, prefer the acronym (e.g., "AWB" not "Automatic White Balance")
8. Only extract entities that are **actually mentioned** in the text

## EXAMPLES:
Good: "Reinforcement Learning", "White Balance", "RL-AWB", "Multi-Sensor Dataset"
Bad: "combining statistical methods", "a novel framework", "remains a challenging problem"

Good evidence: "using deep reinforcement learning for color constancy"
Bad evidence: "We present RL-AWB, a novel framework combining statistical methods with deep reinforcement learning for nighttime white balance"
"""

USER_PROMPT = """Extract entities from this abstract:

{abstract}

Remember: Extract specific technical terms in Title Case, not long phrases."""


class LLMService:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            api_key=api_key,
            model="gemini-3-flash-preview",
            temperature=0
        )

        self.structured_llm = self.llm.with_structured_output(PaperExtractionSchema)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT)
        ])

    async def extract_entities(self, abstract: str) -> PaperExtractionSchema:
        chain = self.prompt | self.structured_llm
        result = await chain.ainvoke({"abstract": abstract})
        return result