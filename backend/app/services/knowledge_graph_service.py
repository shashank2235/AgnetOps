from app.schemas.graph import GraphContextOut


class KnowledgeGraphService:
    async def get_related_context(self, query: str) -> GraphContextOut:
        entities = [
            {"id": "entity:med_policy_101", "name": "Medical Policy 101", "type": "Policy"},
            {"id": "entity:cardiology", "name": "Cardiology", "type": "Specialty"},
        ]
        relations = [
            {"from": "entity:med_policy_101", "to": "entity:cardiology", "type": "covers"},
        ]
        linked_chunk_ids = ["chunk-001", "chunk-002", "chunk-003"]
        return GraphContextOut(entities=entities, relations=relations, linked_chunk_ids=linked_chunk_ids)
