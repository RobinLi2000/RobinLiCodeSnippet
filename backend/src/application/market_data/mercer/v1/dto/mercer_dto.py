from pydantic import BaseModel

from ......domain.entity.mercer.enums.mercer_grade_with_description import (
    MercerGradeWithDescription,
)


class MercerDTO(BaseModel):
    jobCode: str | None = None
    jobTitle: str | None = None
    jobDescription: str | None = None
    grade: MercerGradeWithDescription | None = None
    familyCode: str | None = None
    familyTitle: str | None = None
    subFamilyCode: int | None = None
    subFamilyTitle: str | None = None
    specializationCode: str | None = None
    specializationTitle: str | None = None
    specializationDescription: str | None = None
    industry: str | None = None
    careerLevelTitle: str | None = None
    typicalTitle: str | None = None
    occupationNum: int | None = None

    class Config:
        frozen = False

        
