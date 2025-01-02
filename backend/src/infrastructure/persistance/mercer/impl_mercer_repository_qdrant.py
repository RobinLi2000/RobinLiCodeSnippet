from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchValue,
    MatchText,
    MatchAny,
    ScoredPoint,
)

from .... import config
from ....domain.entity.mercer.repository.mercer_repository_vector import (
    MercerRepositoryVector,
)
from ....domain.entity.mercer.models.mercer import Mercer


class ImplMercerRepositoryVector(MercerRepositoryVector):
    def __init__(
        self,
    ):
        self.client = self._create_client()
        self.collection_name = "specializationDescription1024"

    def _create_client(self):
        client = QdrantClient(config.QDRANT_BASE, port=config.QDRANT_PORT)
        return client

    def _map_to_do(self, result: list[ScoredPoint]) -> list[Mercer]:
        for i, hit in enumerate(result):
            result[i] = Mercer(
                **hit.payload,
            )
        return result

    def _check_not_empty(self, value: str | list[str]) -> bool:
        return (
            value is not None
            and value != ""
            and value != []
            and None not in list(value)
        )

    def query(
        self,
        embeddeding: list[float],
        filter_condition: dict[str, str | list[str]] | None = None,
        search_condition: dict[str, str | list[str]] | None = None,
        limit: int = 50,
        # sort_by: str = "",
        # sort_order: Literal["asc", "desc"] = "desc",
    ):
        should = []
        if filter_condition:
            should.extend(
                [
                    FieldCondition(
                        key=key,
                        match=(
                            MatchValue(text=value)
                            if type(value) is str
                            else MatchAny(any=value)
                        ),
                    )
                    for key, value in filter_condition.items()
                    if self._check_not_empty(value)
                ]
            )

        if search_condition:
            should.extend(
                [
                    FieldCondition(
                        key=key,
                        match=(
                            MatchText(text=value)
                            if type(value) is str
                            else MatchText(text=" ".join(value))
                        ),
                    )
                    for key, value in search_condition.items()
                    if self._check_not_empty(value)
                ]
            )

        print(should)

        query_filter = Filter(must=should)

        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=embeddeding,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

        result = self._map_to_do(result)

        # if sort_by and sort_order:
        #     result = sorted(
        #         result,
        #         key=lambda x: x.payload.get(sort_by, 0),
        #         reverse=sort_order == "desc",
        #     )

        return result
