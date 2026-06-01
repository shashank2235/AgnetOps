from openai import AsyncAzureOpenAI, AsyncOpenAI

from app.core.config import settings


class LLMService:
    def __init__(self) -> None:
        self._openai_client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        self._azure_client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )

    async def generate_medical_response(
        self,
        query: str,
        context_chunks: list[str],
        graph_entities: list[dict],
    ) -> str:
        prompt = (
            "You are a medical document review assistant. "
            "Answer with policy-grounded guidance, avoid unsafe diagnosis/prescription, "
            "and include citations to context chunk IDs.\n\n"
            f"User query: {query}\n"
            f"Context chunks: {context_chunks}\n"
            f"Graph entities: {graph_entities}\n"
            "Return concise answer with a 'Citations:' line."
        )

        try:
            if settings.azure_openai_enabled:
                completion = await self._azure_client.chat.completions.create(
                    model=settings.azure_openai_deployment,
                    messages=[
                        {"role": "system", "content": "You provide safe, policy-grounded medical document summaries."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )
            else:
                completion = await self._openai_client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[
                        {"role": "system", "content": "You provide safe, policy-grounded medical document summaries."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                )

            content = completion.choices[0].message.content
            if content is None:
                raise RuntimeError("Model returned an empty response")
            return content
        except Exception:
            citations = ", ".join(context_chunks) if context_chunks else "no context"
            entities = ", ".join(entity.get("name", "unknown") for entity in graph_entities) if graph_entities else "no graph entities"
            return (
                f"Policy-grounded guidance for: {query}. "
                f"Use clinician review for medication or diagnostic decisions. "
                f"Context: {citations}. Graph entities: {entities}.\n"
                f"Citations: {citations}"
            )
