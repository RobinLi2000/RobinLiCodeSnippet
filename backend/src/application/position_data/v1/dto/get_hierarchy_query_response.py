from pydantic import BaseModel

from .....domain.entity.position.models.position import Position


class GetHierarchyQueryResponse(BaseModel):
    parent: list[Position]
    children: list[Position]
