from pydantic import BaseModel


class GetHierarchyQuery(BaseModel):
    position_code: str
