from abc import ABC, abstractmethod

from ..models.mercer import Mercer
from ..models.template import Template


class MercerRepositoryFullText(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def query_cross_search_async(
        self,
        keywords: dict[str, list[str]],
        fields: dict[str, list[str]],
        filter_condition: dict[str, str | list[str]],
        jd_embedding: list[float] | None = None,
        title_embedding: list[float] | None = None,
        limit: int = 50,
    ) -> list[Mercer]:
        pass

    @abstractmethod
    async def get_template_data_by_job_code_async(
        self, job_code: str
    ) -> Template | None:
        pass
