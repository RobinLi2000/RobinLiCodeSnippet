from fastapi import APIRouter, Request

from ......infrastructure.persistance.mercer.impl_mercer_repository_es import (
    ImplMercerRepositoryFullText,
)
from ..controller.get_template_controller import GetTemplateController
from ..query.handler.get_template_query_handller import GetTemplateQueryHandller

router = APIRouter()


@router.get("/mercer/template")
async def mercer_template(request: Request, job_code: str):
    repository = ImplMercerRepositoryFullText(es_client=request.app.state.es_client)
    query_handler = GetTemplateQueryHandller(repository=repository)
    controller = GetTemplateController(query_handler=query_handler)

    template = await controller.get(job_code=job_code)

    return template
