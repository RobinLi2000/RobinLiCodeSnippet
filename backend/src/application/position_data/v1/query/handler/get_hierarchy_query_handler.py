import asyncio

from ..get_hierarchy_query import GetHierarchyQuery
from ......domain.entity.position.repository.position_repository import (
    PositionRepository,
)
from ...dto.get_hierarchy_query_response import GetHierarchyQueryResponse


class GetHierarchyQueryHandler:
    def __init__(self, repository: PositionRepository):
        self.repository = repository

    async def query(self, query: GetHierarchyQuery):
        parent, children = await asyncio.gather(
            self.repository.get_parent_async(query.position_code),
            self.repository.get_children_async(query.position_code),
        )

        return GetHierarchyQueryResponse(parent=parent, children=children)
