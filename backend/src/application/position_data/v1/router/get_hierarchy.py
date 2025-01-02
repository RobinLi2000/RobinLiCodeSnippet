from typing import Annotated

from fastapi import APIRouter, Query, Request

from .....infrastructure.persistance.position.impl_position_repository import (
    ImplPositionRepository,
)
from ..controller.get_hierarchy_controller import GetHierarchyController
from ..query.get_hierarchy_query import GetHierarchyQuery
from ..query.handler.get_hierarchy_query_handler import GetHierarchyQueryHandler

router = APIRouter()


@router.get("/hierarchy")
async def get_hierarchy(request: Request, body: Annotated[GetHierarchyQuery, Query()]):
    repositiory = ImplPositionRepository(es_client=request.app.state.es_client)
    query_handler = GetHierarchyQueryHandler(repository=repositiory)
    controller = GetHierarchyController(query_handler=query_handler)
    return await controller.get(query=body)
