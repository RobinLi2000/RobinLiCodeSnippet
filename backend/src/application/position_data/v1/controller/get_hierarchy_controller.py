from ..query.get_hierarchy_query import GetHierarchyQuery
from ..query.handler.get_hierarchy_query_handler import GetHierarchyQueryHandler


class GetHierarchyController:
    def __init__(self, query_handler: GetHierarchyQueryHandler):
        self.query_handler = query_handler

    async def get(self, query: GetHierarchyQuery):
        return await self.query_handler.query(query)
