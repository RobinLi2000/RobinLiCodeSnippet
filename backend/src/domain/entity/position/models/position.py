from pydantic import BaseModel


class Position(BaseModel):
    businessLine: str | None
    division: str | None
    grade: str | None
    jobFunction: str | None
    jobTitle: str | None
    locationGroup: str | None
    marketDataSource: str | None
    marketJobCode: str | None
    marketJobCodeName: str | None
    marketPayPosition: str | None
    marketPeerGroup: str | None
    parentPositionCode: str | None
    positionCode: str
