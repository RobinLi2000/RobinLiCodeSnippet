from ......domain.entity.position.models.position import Position
from ......domain.entity.position.repository.position_repository import (
    PositionRepository,
)
from ..get_position_query import GetPositionQuery, CountPositionQuery


class GetPositionHandler:
    def __init__(self, repository: PositionRepository):
        self.repository = repository

    async def query(self, query: GetPositionQuery) -> list[Position]:
        match query.by:
            case "JOB_CODE":
                return await self.repository.get_by_job_code_async(
                    query.value, data_source=query.source
                )
            case "POSITION_CODE":
                # return await self.repository.get_by_position_code_async(query)
                return []
            case _:
                return None

    async def count(self, query: CountPositionQuery) -> list[Position]:
        match query.by:
            case "JOB_CODE":
                return await self.repository.get_occupation_count_by_job_codes(
                    job_codes=query.values, source=query.source
                )
            case "POSITION_CODE":
                # return await self.repository.get_by_position_code_async(query)
                return 0
            case _:
                return None
