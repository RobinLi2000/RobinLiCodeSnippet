import logging

from .....position_data.v1.query.handler.get_position_query_handler import (
    GetPositionHandler,
)
from ..dto.query_request_dto import QueryRequestDTO
from ..enums.steps import Steps
from ..query.handler.rank_data_query_handler import RankDataQueryHandler
from ..query.rank_data_query import RankDataQuery

logger = logging.getLogger(__name__)


class QueryController:
    def __init__(
        self,
        key: str,
        request: QueryRequestDTO,
        query_handler: RankDataQueryHandler,
        position_handler: GetPositionHandler,
    ):
        self.key = key
        self.request = request
        self.query_handler = query_handler
        self.logger = logging.getLogger(__name__)
        self.position_handler = position_handler

    async def run(self):
        if self.request.stream:
            return self._stream_results()
        else:
            final_result = None
            async for result in self._stream_results():
                final_result = result

            return final_result

    async def _stream_results(self):
        yield Steps.EXTRACT.value

        subfamilies, keywords = await self.query_handler.generate_ai_artifacts(
            self.key, self.request.query.title, self.request.query.jd
        )

        # logger.info(f"Title subfamilies: {subfamilies["title_subfamilies"]}")
        # logger.info(f"JD subfamilies: {subfamilies["jd_subfamilies"]}")

        # logger.info(f"Title Keywords: {keywords["title_keywords"]}")
        # logger.info(f"JD Keywords: {keywords['jd_keywords']}")

        yield Steps.RETURN.value

        results = await self.query_handler.query(
            query=RankDataQuery(
                key=self.key,
                jd=self.request.query.jd,
                title=self.request.query.title,
                subfamilies=subfamilies,
                keywords=keywords,
                jebsen_grade=self.request.query.grade,
                mercer_filter=self.request.filter,
                limit=self.request.limit,
                semantics_weight=self.request.query.semantic_weight,
                keywords_weight=self.request.query.keyword_weight,
                title_importance=self.request.query.title_importance,
            )
        )

        if self.request.page and self.request.page_size:
            paginated_results, total_page_num = self.query_handler.paginate(
                results, self.request.page, self.request.page_size
            )

        else:
            paginated_results = results
            total_page_num = 1

        yield f"total_page_num: {str(total_page_num)}"
        yield paginated_results
