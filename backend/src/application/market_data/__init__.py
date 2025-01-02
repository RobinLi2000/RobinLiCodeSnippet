from fastapi import APIRouter
from .mercer.v1.router.query import router as mercer_v1_query
from .mercer.v1.router.template import router as mercer_v1_template

router = APIRouter(prefix="/v1/market-data")

router.include_router(mercer_v1_query)
router.include_router(mercer_v1_template)
