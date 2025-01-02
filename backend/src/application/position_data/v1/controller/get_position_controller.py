from ..query.get_position_query import GetPositionQuery
from ..query.handler.get_position_query_handler import GetPositionHandler


class GetPositionController:
    def __init__(self, query_handler: GetPositionHandler):
        self.query_handler = query_handler

    async def get(self, query: GetPositionQuery):
        return await self.query_handler.query(query)
