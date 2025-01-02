import asyncio
import logging
import math

from elasticsearch import AsyncElasticsearch

from .......domain.common.enums.company_grade import JebsenGrade
from .......domain.common.repository.cache import Cache
from .......domain.entity.mercer.repository.mercer_repository_full_text import (
    MercerRepositoryFullText,
)
from .......domain.entity.mercer.service.jebsen_grade_converter import (
    convert_grade_from_jebsen_to_mercer,
)
from .......infrastructure.service.embedding import AzureOpenAIEmbeddingAda
from ...dto.mercer_dto import MercerDTO
from ...mapping.do_to_dto import mercer_do_to_dto
from ...service.ai import generate_keywords, generate_subfamily
from ..rank_data_query import RankDataQuery

logger = logging.getLogger(__name__)

class RankDataQueryHandler:
    def __init__(
        self,
        # repository_vector: MercerRepositoryVector,
        repository_full_text: MercerRepositoryFullText,
        cache: Cache,
        es_client: AsyncElasticsearch,
    ):
        # self.repository_vector = repository_vector
        self.repository_full_text = repository_full_text
        self.cache = cache
        self.es_client = es_client

    async def query(self, query: RankDataQuery) -> list[MercerDTO]:
        filter_condition = {}
        filter_condition["levelCode"] = self._get_level_code(
            query.mercer_filter, query.jebsen_grade
        )

        search_condition = {}
        if query.mercer_filter:
            search_condition.update(
                {k: v for k, v in query.mercer_filter.model_dump().items()}
            )
            search_condition.pop("grade")
        for k, v in search_condition.items():
            if v is not None:
                filter_condition[k] = v
                
        # logger.info("Filter condition: %s", filter_condition)
        # logger.info("Search condition: %s", search_condition)

        # result_search_by_semantics = await self._query_data_by_specialization_semantics(
        #     query.jd, filter_condition, search_condition, query.limit
        # )

        # result_search_by_semantics = []
        result_search_by_keywords = await self._query_data_es(
            jd=query.jd,
            title=query.title,
            keywords=query.keywords,
            subfamilies=query.subfamilies,
            filter_condition=filter_condition,
            limit=query.limit,
            semantics_weight=query.semantics_weight,
            keywords_weight=query.keywords_weight,
            title_importance=query.title_importance
        )
        # result_search_by_keywords = []

        return result_search_by_keywords

        # return self._merge_and_rerank(
        #     result_search_by_semantics,
        #     result_search_by_keywords,
        #     query.subfamily,
        #     query.semantics_weight,
        #     query.keywords_weight,
        #     query.subfamily_bonus,
        # )

    def paginate(
        self, results: list[MercerDTO], page: int, page_size: int
    ) -> tuple[list[MercerDTO], int]:
        start = (page - 1) * page_size
        end = start + page_size
        total_page_num = math.ceil(len(results) / page_size)
        # logger.info(f"total_page_num: {total_page_num}")

        return results[start:end], total_page_num

    async def generate_ai_artifacts(self, key: str, title: str, jd: str):
        return await asyncio.gather(
            generate_subfamily(key, title, jd, self.cache),
            generate_keywords(key, title, jd, self.cache),
        )

    def _get_level_code(
        self, mercer_filter: MercerDTO, jebsen_grade: JebsenGrade
    ) -> list[str]:
        if not mercer_filter or not mercer_filter.grade:
            grade = convert_grade_from_jebsen_to_mercer(jebsen_grade)
            return [g.value for g in grade]
        else:
            return [mercer_filter.grade.value.split(" ")[0]]

    # def _merge_and_rerank(
    #     self,
    #     result_search_by_semantics: list[MercerDTO],
    #     result_search_by_keywords: list[MercerDTO],
    #     subfamily: list[str],
    #     semantics_weight: float = 0.5,
    #     keywords_weight: float = 0.5,
    #     subfamily_bonus: float = 50,
    # ) -> list[MercerDTO]:
    #     scores: DefaultDict[str, float] = defaultdict(float)

    #     def update_score(items: list[MercerDTO], weight: float):
    #         for index, item in enumerate(items):
    #             scores[item] += (len(items) - index) * weight + (
    #                 subfamily_bonus / 2 if item.subFamilyTitle in subfamily else 0
    #             )

    #     update_score(result_search_by_semantics, semantics_weight)
    #     update_score(result_search_by_keywords, keywords_weight)

    #     ranked_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    #     return [item for item, _ in ranked_items]

    # async def _query_data_by_specialization_semantics(
    #     self,
    #     jd,
    #     filter_condition: dict[str, str | list[str]] = None,
    #     search_condition: dict[str, str | list[str]] = None,
    #     limit: int = 100,
    # ):
    #     embedding = await AzureOpenAIEmbeddingAda()(jd)

    #     result = self.repository_vector.query(
    #         embeddeding=embedding,
    #         filter_condition=filter_condition,
    #         search_condition=search_condition,
    #         limit=limit,
    #     )

    #     result: list[MercerDTO] = mercer_do_to_dto(result)
    #     return result

    async def _query_data_es(
        self,
        jd: str,
        title: str,
        keywords: dict[str, list[str]],
        subfamilies: dict[str, list[str]],
        # es_clinet: AsyncElasticsearch,
        filter_condition: dict[str, str | list[str]] = None,
        limit: int = 100,
        semantics_weight: float = 0.5,
        keywords_weight: float = 0.5,
        title_importance: float = 0.5
    ):
        jd_embedding, title_embedding = await asyncio.gather(
            AzureOpenAIEmbeddingAda()(jd), AzureOpenAIEmbeddingAda()(title)
        )
        result = await self.repository_full_text.query_cross_search_async(
            keywords=keywords,
            subfamilies=subfamilies,
            fields=[
                "jobTitle",
                "typicalTitle",
                "specializationDescription",
                "industry",
                "level",
            ],
            filter_condition=filter_condition,
            jd_embedding=jd_embedding,
            title_embedding=title_embedding,
            limit=limit,
            semantics_weight=semantics_weight,
            keywords_weight=keywords_weight,
            title_importance=title_importance
        )

        result: list[MercerDTO] = mercer_do_to_dto(result)
        return result
