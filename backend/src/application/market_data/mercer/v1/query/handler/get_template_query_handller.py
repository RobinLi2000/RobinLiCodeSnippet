from .......domain.entity.mercer.repository.mercer_repository_full_text import (
    MercerRepositoryFullText,
)
from .......domain.entity.mercer.models.template import Template
from ..get_template_query import GetTemplateQuery


class GetTemplateQueryHandller:
    def __init__(self, repository: MercerRepositoryFullText):
        self.repository = repository

    async def query(self, query: GetTemplateQuery) -> Template | None:
        template = await self.repository.get_template_data_by_job_code_async(
            query.job_code
        )
        return template
