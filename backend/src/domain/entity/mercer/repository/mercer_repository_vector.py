from abc import ABC, abstractmethod

from ..models.mercer import Mercer


class MercerRepositoryVector(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def query(
        self,
        embeddeding: list[float],
        filter_condition: dict[str, str | list[str]] | None = None,
        search_condition: dict[str, str | list[str]] | None = None,
        limit: int = 50,
    ) -> list[Mercer]:
        pass
