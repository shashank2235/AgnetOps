from pydantic import BaseModel


class GraphContextOut(BaseModel):
    entities: list[dict]
    relations: list[dict]
    linked_chunk_ids: list[str]
