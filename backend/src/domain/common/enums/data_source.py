from enum import Enum


class DataSource(str, Enum):
    AON_HEWITT = "Aon Hewitt"
    MERCER = "Mercer"
    MCLAGAN = "McLagan"
    KORN_FERRY_HAY_GROUP = "Korn Ferry Hay Group"
    WILLIS_TOWERS_WATSON = "Willis Towers Watson"
