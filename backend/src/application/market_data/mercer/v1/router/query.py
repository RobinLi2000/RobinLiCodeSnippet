import json
from typing import AsyncGenerator, Union

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ......infrastructure.persistance.common.impl_cache import ImplCache
from ......infrastructure.persistance.mercer.impl_mercer_repository_es import (
    ImplMercerRepositoryFullText,
)
from ......infrastructure.persistance.position.impl_position_repository import (
    ImplPositionRepository,
)
from .....position_data.v1.query.handler.get_position_query_handler import (
    GetPositionHandler,
)
from ..controller.query_controller import QueryController
from ..dto.query_request_dto import QueryRequestDTO
from ..query.handler.rank_data_query_handler import RankDataQueryHandler

router = APIRouter()
import logging  # noqa: E402


@router.post("/mercer/query")
async def mercer_query(request: Request, body: QueryRequestDTO):
    logging.info(f"request body, str({body})")
    user_data = request.state.user
    key = f"{user_data.get('tid')}{user_data.get('sub')}"
    es_client = request.app.state.es_client
    # repository_vector = ImplMercerRepositoryVector()
    repository_es_mercer = ImplMercerRepositoryFullText(es_client=es_client)
    repository_es_position = ImplPositionRepository(es_client=es_client)
    cache = ImplCache()

    query_handler = RankDataQueryHandler(
        # repository_vector=repository_vector,
        repository_full_text=repository_es_mercer,
        cache=cache,
        es_client=es_client,
    )

    position_handler = GetPositionHandler(
        repository=repository_es_position
    )

    controller = QueryController(key=key, request=body, query_handler=query_handler, position_handler=position_handler)

    if body.stream:

        async def stream_response() -> AsyncGenerator[str, None]:
            try:
                chunks: AsyncGenerator[
                    Union[str, list[BaseModel]]
                ] = await controller.run()
                async for chunk in chunks:
                    if isinstance(chunk, str):
                        if "total_page_num" in chunk:
                            page_num = chunk.split(":")[-1].strip()
                            yield f"data:{json.dumps({'total_page_num': page_num})}\n\n"
                        else:
                            yield f"data:{json.dumps({'stage': chunk})}\n\n"
                    else:
                        for item in chunk:
                            yield f"data:{item.model_dump_json()}\n\n"
            except Exception as e:
                yield f"data:{json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(stream_response(), media_type="text/event-stream")

    try:
        return await controller.run()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
