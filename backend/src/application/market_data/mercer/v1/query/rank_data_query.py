from pydantic import BaseModel

from ......domain.common.enums.company_grade import JebsenGrade

# from ..dto.mercer_dto import MercerDTO
from ..dto.query_request_dto import QueryFilterDTO


class RankDataQuery(BaseModel):
    key: str
    jd: str
    title: str
    keywords: dict[str, list[str]]
    subfamilies: dict[str, list[str]]
    jebsen_grade: JebsenGrade
    mercer_filter: QueryFilterDTO | None
    semantics_weight: float = 0.5
    keywords_weight: float = 0.5
    title_importance: float = 0.5
    limit: int = 100
