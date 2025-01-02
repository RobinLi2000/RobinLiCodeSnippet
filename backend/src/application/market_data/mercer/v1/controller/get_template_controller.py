from ..query.get_template_query import GetTemplateQuery
from ..query.handler.get_template_query_handller import GetTemplateQueryHandller


class GetTemplateController:
    def __init__(self, query_handler: GetTemplateQueryHandller):
        self.query_handler = query_handler

    async def get(self, job_code: str):
        query = GetTemplateQuery(job_code=job_code)
        return await self.query_handler.query(query)
