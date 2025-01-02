from elasticsearch import AsyncElasticsearch

from .... import config
from ....domain.common.enums.data_source import DataSource
from ....domain.entity.position.models.position import Position
from ....domain.entity.position.repository.position_repository import PositionRepository
import logging


class ImplPositionRepository(PositionRepository):
    def __init__(self, es_client: AsyncElasticsearch):
        self.client = es_client
        self.index = config.POSITION_INDEX
        self.logger = logging.getLogger(__name__)

    # def _create_client(self):
    #     client = AsyncElasticsearch(
    #         hosts=config.ES_BASE,
    #         api_key=config.ES_KEY,
    #         timeout=5,
    #         retry_on_timeout=True,
    #         max_retries=5,
    #     )

    #     return client

    def _map_to_do(self, result: list[dict]) -> list[Position]:
        for i, hit in enumerate(result):
            result[i] = Position(**hit["_source"])

        return result

    async def get_by_job_code_async(self, code: str, data_source: DataSource):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"wildcard": {"marketJobCode": f"*{code}*"}},
                        # {"term": {"marketDataSource": f"{data_source.value}"}},
                    ]
                }
            },
            "size": 1000,
        }

        response = await self.client.search(index=self.index, body=query)
        return self._map_to_do(response["hits"]["hits"])

    async def get_parent_async(self, code: str):
        query = {"query": {"term": {"positionCode": code}}}
        response = await self.client.search(index=self.index, body=query)
        hits = response["hits"]["hits"]
        if not hits:
            return []

        parent_position_code = hits[0]["_source"]["parentPositionCode"]
        if not parent_position_code:
            return []

        query = {"query": {"term": {"positionCode": parent_position_code}}}
        response = await self.client.search(index=self.index, body=query)
        hits = response["hits"]["hits"]
        return self._map_to_do(hits)

    async def get_children_async(self, code: str):
        response = await self.client.search(
            index=self.index, body={"query": {"match": {"parentPositionCode": code}}}
        )
        return self._map_to_do(response["hits"]["hits"])

    async def get_occupation_count_by_job_code(
        self, job_code: str, source: DataSource
    ) -> int:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"wildcard": {"marketJobCode": f"*{job_code}*"}},
                        # {"term": {"marketDataSource": f"{source.value}"}},
                    ]
                }
            }
        }
        response = await self.client.count(index=self.index, body=query)
        return response["count"]

    async def get_occupation_count_by_job_codes(
        self, job_codes: list[str], source: DataSource
    ) -> dict[str, int]:
        should_queries = []
        for code in job_codes:
            should_queries.append(
                {
                    "wildcard": {
                        "marketJobCode": f"*{code}*"  # 在code前后添加*以进行子串匹配
                    }
                }
            )

        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"bool": {"should": should_queries, "minimum_should_match": 1}},
                        # {"term": {"marketDataSource": source.value}},
                    ]
                }
            },
            "aggs": {
                "job_code_counts": {
                    "terms": {
                        "field": "marketJobCode",
                        "size": len(
                            job_codes
                        ),  # 设置为job_codes的长度以返回所有匹配的code
                    }
                }
            },
        }
        # self.logger.info("Count query:", query)
        # self.logger.info("index name:", self.index)
        response = await self.client.search(index=self.index, body=query)
        # self.logger.info(f"count response: {response}")

        # 将结果转换为字典
        result = {
            bucket["key"]: bucket["doc_count"]
            for bucket in response["aggregations"]["job_code_counts"]["buckets"]
        }
        # self.logger.info(f"count result: {result}")
        # 确保所有输入的job_codes都有对应的计数，没有的设为0
        for code in job_codes:
            if not any(code in k for k in result.keys()):
                result[code] = 0

        # self.logger.info(f"final result: {result}")
        return result
