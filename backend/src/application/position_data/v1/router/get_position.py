from typing import Annotated

from fastapi import APIRouter, Query, Request

from .....infrastructure.persistance.position.impl_position_repository import (
    ImplPositionRepository,
)
from ..controller.get_position_controller import GetPositionController
from ..query.get_position_query import GetPositionQuery
from ..query.handler.get_position_query_handler import GetPositionHandler

router = APIRouter()


@router.get("/")
async def position_data(request: Request, body: Annotated[GetPositionQuery, Query()]):
    repositiory = ImplPositionRepository(request.app.state.es_client)
    query_handler = GetPositionHandler(repository=repositiory)
    controller = GetPositionController(query_handler=query_handler)

    return await controller.get(query=body)
