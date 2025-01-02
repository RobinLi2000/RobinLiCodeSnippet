from fastapi import APIRouter

from .v1.router.get_position import router as position_data_v1_get
from .v1.router.get_hierarchy import router as position_data_v1_get_hierarchy

router = APIRouter(prefix="/v1/position-data")

router.include_router(position_data_v1_get)
router.include_router(position_data_v1_get_hierarchy)
