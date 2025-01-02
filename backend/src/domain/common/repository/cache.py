from abc import ABC, abstractmethod


class Cache(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def set_async(self, key, value, expire=3600):
        pass

    @abstractmethod
    async def get_async(self, key):
        pass
