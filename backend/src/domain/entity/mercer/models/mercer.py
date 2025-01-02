from pydantic import BaseModel

from ..enums.mercer_grade import MercerGrade


class Mercer(BaseModel):
    jobCode: str | None = None
    jobTitle: str | None = None
    jobDescription: str | None = None

    familyCode: str | None = None
    familyTitle: str | None = None

    subFamilyCode: int | None = None
    subFamilyTitle: str | None = None

    specializationCode: str | None = None
    specializationTitle: str | None = None
    specializationDescription: str | None = None

    level: str | None = None
    levelCode: MercerGrade | None = None

    industry: str | None = None

    typicalTitle: str | None = None

    careerLevelTitle: str | None = None
    careerStreamTitle: str | None = None

    universalNavigationGroupTitle: str | None = None

    occupationNum: int | None = 0
