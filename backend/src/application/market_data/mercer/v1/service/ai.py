import base64

from .agents import (
    subfamily_determine_agent,
    keyword_extraction_agent,
)

from ......domain.common.repository.cache import Cache
import logging
logger = logging.getLogger(__name__)

async def generate_subfamily(key: str, title: str, jd: str, cache: Cache, topk=10):
    encoded_key = base64.b64encode(f"{key}{title}{jd}subfamily".encode())

    subfamily = await cache.get_async(encoded_key)

    if subfamily:
        logger.info("completed cache.get")
        return subfamily

    subfamily = await subfamily_determine_agent(
        # JD=f"Title: \n{title}\nJob description: \n{jd}",
        JD=jd,
        title=title,
        topk=topk,
    )

    if not subfamily:
        logger.info("no subfamily found")
        return []

    await cache.set_async(encoded_key, subfamily)
    return subfamily


async def generate_keywords(key: str, title: str, jd: str, cache: Cache):
    encoded_key = base64.b64encode(f"{key}{title}{jd}keywords".encode())

    keywords = await cache.get_async(encoded_key)

    if keywords:
        logger.info("completed cache.get")
        return keywords

    keywords = await keyword_extraction_agent(
        # JD=f"Title: \n{title}\nJob description: \n{jd}"
        JD=jd,
        title=title,
    )

    if not keywords:
        logger.info("no keywords found")
        return []

    await cache.set_async(encoded_key, keywords)
    return keywords
