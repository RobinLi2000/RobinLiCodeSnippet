from typing import Optional

from pydantic import BaseModel, Field

from ......domain.common.enums.company_grade import JebsenGrade

# from ..enums.title_importance import TitleImportance
from ......domain.entity.mercer.enums.mercer_grade_with_description import (
    MercerGradeWithDescription,
)


class QueryParametersDTO(BaseModel):
    jd: str
    title: str
    grade: JebsenGrade
    # limit: int = 50
    keyword_weight: float = 0.5
    semantic_weight: float = 0.5
    title_importance: float = 0.5


class OccupationNumRange(BaseModel):
    min: int = Field(0, ge=0)  # 使用Field的ge参数来限制
    max: int = Field(99999, ge=0)


class QueryFilterDTO(BaseModel):
    jobCode: Optional[str] = None
    jobTitle: Optional[str] = None
    jobDescription: Optional[str] = None
    grade: Optional["MercerGradeWithDescription"] = (
        None  # Ensure this is defined correctly
    )
    familyCode: Optional[str] = None
    familyTitle: Optional[str] = None
    subFamilyCode: Optional[int] = None
    subFamilyTitle: Optional[str] = None
    specializationCode: Optional[str] = None
    specializationTitle: Optional[str] = None
    specializationDescription: Optional[str] = None
    industry: Optional[str] = None
    careerLevelTitle: Optional[str] = None
    typicalTitle: Optional[str] = None
    occupationNum: OccupationNumRange = OccupationNumRange()  # Default instance


class QueryRequestDTO(BaseModel):
    stream: bool = True
    sort_by: Optional[str] = "score"
    sort_order: Optional[str] = "desc"
    page: int = 1
    page_size: int = 20
    limit: int = 100
    query: Optional[QueryParametersDTO] = None
    filter: Optional[QueryFilterDTO] = None
