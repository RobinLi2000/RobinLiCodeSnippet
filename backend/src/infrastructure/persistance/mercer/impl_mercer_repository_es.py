import copy
import json
import logging

from elasticsearch import AsyncElasticsearch

from .... import config
from ....domain.entity.mercer.models.mercer import Mercer
from ....domain.entity.mercer.models.template import Template
from ....domain.entity.mercer.repository.mercer_repository_full_text import (
    MercerRepositoryFullText,
)

logger = logging.getLogger(__name__)


class ImplMercerRepositoryFullText(MercerRepositoryFullText):
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client
        self.mercer_index = config.MERCER_INDEX
        self.template_index = config.TEMPLATE_INDEX

    def _map_to_do(self, result: list[dict]) -> list[Mercer]:
        for i, hit in enumerate(result):
            result[i] = Mercer(**hit["_source"])
        return result

    async def query_cross_search_async(
        self,
        keywords: dict[str, list[str]],
        subfamilies: dict[str, list[str]],
        fields: list[str],
        filter_condition: dict[str, str | list[str]],
        jd_embedding: list[float] | None = None,
        title_embedding: list[float] | None = None,
        limit: int = 50,
        semantics_weight: float = 0.5,
        keywords_weight: float = 0.5,
        title_importance: float = 0.5,
    ):
        jd_keywords = keywords["jd_keywords"]
        title_keywords = keywords["title_keywords"]
        jd_subfamilies = subfamilies["jd_subfamilies"]
        title_subfamilies = subfamilies["title_subfamilies"]

        jd_query_string = " ".join(jd_keywords)
        title_query_string = " ".join(title_keywords)

        jd_fuzzy_string = " OR ".join([f'"{keyword}"~2' for keyword in jd_keywords])
        title_fuzzy_string = " OR ".join(
            [f'"{keyword}"~2' for keyword in title_keywords]
        )
        # logger.info(f"Filter condition: {filter_condition}")

        occupationNumFilter = filter_condition.pop("occupationNum", None)

        # logger.info(f"current filter condition: {filter_condition}")

        must_conditions = [
            {
                "wildcard"
                if isinstance(value, str) and key != "levelCode"
                else "terms": {
                    f"{key}.keyword" if key != "levelCode" else key: f"*{value}*"
                    if isinstance(value, str) and key != "levelCode"
                    else value
                }
            }
            for key, value in filter_condition.items()
            if value is not None
            and value != ""
            and value != []
            and None not in list(value)
        ]

        if occupationNumFilter:
            must_conditions.append(
                {
                    "range": {
                        "occupationNum": {
                            "gte": occupationNumFilter["min"],
                            "lte": occupationNumFilter["max"],
                        }
                    }
                }
            )

        normal_query = {
            "_source": {"excludes": "specializationVector"},
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": jd_query_string,
                                "fields": fields,
                                "fuzziness": "AUTO",
                                "boost": 1.0 - title_importance,
                            }
                        },
                        {
                            "multi_match": {
                                "query": title_query_string,
                                "fields": fields,
                                "fuzziness": "AUTO",
                                "boost": title_importance,
                            }
                        },
                        {
                            "query_string": {
                                "query": jd_fuzzy_string,
                                "fields": fields,
                                "boost": 1.0 - title_importance,
                            }
                        },
                        {
                            "query_string": {
                                "query": title_fuzzy_string,
                                "fields": fields,
                                "boost": title_importance,
                            }
                        },
                    ],
                    "minimum_should_match": 0,
                    "must": must_conditions,
                }
            },
        }

        # Adding subFamilyTitle boost
        subfamily_boost_query = {
            "function_score": {
                "query": normal_query["query"],
                "functions": [
                    {
                        "filter": {
                            "terms": {
                                "subFamilyTitle.keyword": jd_subfamilies
                                + title_subfamilies
                            }
                        },
                        "weight": 1.25,  # Adjust the weight as needed
                    }
                ],
                "boost_mode": "sum",
            }
        }

        # logger.info(f"subfamily boost query: {str(subfamily_boost_query)}")

        # knn_query = None
        # if embedding:
        #     knn_query = {
        #         "query": {
        #             "knn": {
        #                 "field": "specializationVector",
        #                 "query_vector": embedding,
        #                 "num_candidates": limit,
        #                 "boost": semantics_weight
        #                 if (1 - semantics_weight == keywords_weight)
        #                 else (1 - keywords_weight),
        #                 "filter": {
        #                     "bool": {"must": [subfamily_boost_query]}
        #                 },
        #             },
        #         },
        #         "collapse": {"field": "jobCode.keyword"},
        #     }
        knn_query = None
        if jd_embedding is not None or title_embedding is not None:
            # 计算向量搜索的总体权重
            vector_weight = (
                semantics_weight
                if (1 - semantics_weight == keywords_weight)
                else (1 - keywords_weight)
            )

            should_conditions = []

            if jd_embedding is not None:
                should_conditions.append(
                    {
                        "knn": {
                            "field": "specializationVector",
                            "query_vector": jd_embedding,
                            "num_candidates": 2 * limit,
                            "boost": vector_weight * (1 - title_importance),  # JD的权重
                        }
                    }
                )

            if title_embedding is not None:
                should_conditions.append(
                    {
                        "knn": {
                            "field": "specializationVector",
                            "query_vector": title_embedding,
                            "num_candidates": 2 * limit,
                            "boost": vector_weight * title_importance,  # title的权重
                        }
                    }
                )

            knn_query = {
                "query": {
                    "bool": {
                        "should": should_conditions,
                        "minimum_should_match": 0,
                        "filter": {"bool": {"must": [subfamily_boost_query]}},
                    }
                },
                "collapse": {"field": "jobCode.keyword"},
            }

        print_query = copy.deepcopy(knn_query if knn_query else subfamily_boost_query)
        try:
            for _ in print_query["query"]["bool"]["should"]:
                _["knn"]["query_vector"] = "xxxxxx"
        except KeyError:
            pass

        # logger.debug(
        #     "ES Query Body with vector: %s",
        #     json.dumps(print_query, indent=2)
        #     if knn_query
        #     else json.dumps(subfamily_boost_query, indent=2),
        # )

        try:
            hits = await self.es_client.search(
                index=self.mercer_index,
                body=knn_query if knn_query else subfamily_boost_query,
                size=limit,
            )

        except Exception as e:
            print(f"Error executing search: {e}")
            return []

        result = self._map_to_do(hits["hits"]["hits"])
        return result

    async def get_template_data_by_job_code_async(
        self, job_code: str
    ) -> Template | None:
        query = {"query": {"term": {"jobCode": job_code}}}
        response = await self.es_client.search(index=self.template_index, body=query)
        hits = response["hits"]["hits"]
        if len(hits) > 0:
            return Template(**hits[0]["_source"])
        else:
            return None
