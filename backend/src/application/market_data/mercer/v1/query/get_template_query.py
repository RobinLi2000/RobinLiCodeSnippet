from pydantic import BaseModel


class GetTemplateQuery(BaseModel):
    job_code: str
