from typing import Union

from ......domain.entity.mercer.models.mercer import Mercer
from ......domain.entity.mercer.enums.mercer_grade_with_description import (
    MercerGradeWithDescription,
)
from ..dto.mercer_dto import MercerDTO


def mercer_do_to_dto(
    do: Union[Mercer, list[Mercer]],
) -> Union[MercerDTO, list[MercerDTO]]:
    if isinstance(do, Mercer):
        return MercerDTO(**do.model_dump())
    elif isinstance(do, list):
        return [
            MercerDTO(
                **do_item.model_dump(),
                grade=MercerGradeWithDescription[do_item.levelCode],
            )
            for do_item in do
        ]
    else:
        raise TypeError
