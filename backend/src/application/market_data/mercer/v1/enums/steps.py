from enum import Enum


class Steps(str, Enum):
    EXTRACT = "EXTRACT"
    RETURN = "RETURN"
    ERROR = "ERROR"

