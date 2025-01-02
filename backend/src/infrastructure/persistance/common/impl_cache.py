from fastapi_cache import FastAPICache

from ....domain.common.repository.cache import Cache


class ImplCache(Cache):
    def __init__(self):
        self.backend = FastAPICache.get_backend()

    async def set_async(self, key, value, expire=3600):
        try:
            await self.backend.set(key, value, expire)
            return True
        except Exception as e:
            print(f"Error setting cache: {str(e)}")
            return False

    async def get_async(self, key):
        try:
            return await self.backend.get(key)
        except Exception as e:
            print(f"Error getting cache: {str(e)}")
            return None
