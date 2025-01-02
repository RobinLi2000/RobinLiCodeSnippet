from typing import Literal, List

from pydantic import BaseModel

from .....domain.common.enums.data_source import DataSource


class GetPositionQuery(BaseModel):
    by: Literal["JOB_CODE", "POSITION_CODE"] = "JOB_CODE"
    value: str
    source: DataSource = DataSource.MERCER

class CountPositionQuery(BaseModel):
    by: Literal["JOB_CODE", "POSITION_CODE"] = "JOB_CODE"
    values: List[str]
    source: DataSource = DataSource.MERCER
    min: int = 0
    max: int = 100
