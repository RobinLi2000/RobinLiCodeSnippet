from abc import ABC, abstractmethod

from ....common.enums.data_source import DataSource
from ..models.position import Position


class PositionRepository(ABC):
    @abstractmethod
    def __init__(self):
        pass

    # @abstractmethod
    # async def get_by_position_code_async(self, code: str) -> list[Position]:
    #     raise NotImplementedError

    @abstractmethod
    async def get_by_job_code_async(
        self, code: str, data_source: DataSource
    ) -> list[Position]:
        raise NotImplementedError

    @abstractmethod
    async def get_parent_async(self, code: str) -> list[Position]:
        raise NotImplementedError

    @abstractmethod
    async def get_children_async(self, code: str) -> list[Position]:
        raise NotImplementedError

    @abstractmethod
    async def get_occupation_count_by_job_codes(
        self, job_codes: list[str], source: DataSource
    ) -> dict[str, int]:
        raise NotImplementedError
