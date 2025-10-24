"""Retrieval service for RAG."""

from typing import Any
from app.models.schemas import Citation
from app.rag import vector_store_service
from app.services.llm import llm_service
from app.services.prompts import prompt_service


class RetrievalService:
    """Service for retrieving relevant information from KB."""

    def __init__(self) -> None:
        """Initialize retrieval service."""
        pass

    def retrieve(
        self,
        query: str,
        tenant: str,
        k: int = 6,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], list[Citation]]:
        """Retrieve relevant chunks from vector store."""
        results = vector_store_service.search(
            query=query,
            tenant=tenant,
            k=k,
            filters=filters,
        )

        # Convert to citations
        citations = []
        for result in results:
            metadata = result["metadata"]
            citation = Citation(
                doc=metadata.get("filename", "Unknown"),
                page=metadata.get("page_number"),
                snippet=result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                score=result.get("score"),
            )
            citations.append(citation)

        return results, citations

    def answer_question(
        self,
        question: str,
        tenant: str,
        filters: dict[str, Any] | None = None,
    ) -> tuple[str, list[Citation]]:
        """Answer a question using RAG."""
        # Retrieve context
        results, citations = self.retrieve(question, tenant, filters=filters)

        if not results:
            return "I don't have that information in my knowledge base.", []

        # Build context
        context_parts = []
        for idx, result in enumerate(results, 1):
            metadata = result["metadata"]
            doc = metadata.get("filename", "Unknown")
            page = metadata.get("page_number")
            content = result["content"]

            context_parts.append(f"[{idx}] Document: {doc}")
            if page:
                context_parts.append(f"    Page: {page}")
            context_parts.append(f"    Content: {content}")
            context_parts.append("")

        context = "\n".join(context_parts)

        # Generate answer
        system_prompt = prompt_service.get_system_prompt("rag_answer")
        user_prompt = prompt_service.format_prompt(
            "rag_answer",
            context=context,
            question=question,
        )

        answer = llm_service.generate(user_prompt, system_prompt)

        return answer, citations

    def validate_entities_with_kb(
        self,
        entities: dict[str, Any],
        tenant: str,
    ) -> tuple[bool, list[Citation]]:
        """Validate entities against KB."""
        # Build validation query
        entity_parts = []
        for key, value in entities.items():
            if value:
                if isinstance(value, list):
                    entity_parts.append(f"{key}: {', '.join(map(str, value))}")
                else:
                    entity_parts.append(f"{key}: {value}")

        query = f"Validate availability: {', '.join(entity_parts)}"

        # Retrieve relevant KB info
        results, citations = self.retrieve(query, tenant, k=4)

        if not results:
            return False, []

        # Build KB context
        kb_context = "\n\n".join([r["content"] for r in results])

        # Use LLM to validate
        system_prompt = prompt_service.get_system_prompt("validate_kb")
        user_prompt = prompt_service.format_prompt(
            "validate_kb",
            entities=str(entities),
            kb_context=kb_context,
        )

        try:
            validation_result = llm_service.generate_json(user_prompt, system_prompt)
            is_valid = validation_result.get("valid", False)
            return is_valid, citations
        except Exception:
            # If validation fails, assume valid with citations
            return True, citations


# Global retrieval service
retrieval_service = RetrievalService()
