from datetime import date
from pydantic import BaseModel


class Template(BaseModel):
    jobTitle: str
    jobType: str
    jobCode: str
    typicalTitle: str
    dataEffectiveDate: date
    currency: str
    displayedIn: str
    totalCashTargetNumOrgs: int
    totalCashTargetNumObs: int
    attcp25: int
    attcp50: int
    attcp75: int