import logging
from typing import Any

from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed
import openai

from .... import config


class AzureOpenAIEmbedding:
    def __init__(self, model: str = "text-embedding-ada-002") -> None:
        self.model = model
        self.client = openai.AsyncAzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
        )

    @retry(
        stop=(stop_after_delay(120) | stop_after_attempt(3)),
        wait=wait_fixed(1),
        retry_error_callback=lambda retry_state: None,
    )
    async def __call__(self, content: str) -> Any:
        try:
            response = await self.client.embeddings.create(
                input=content, model=self.model
            )
            embedding = response.data[0].embedding
            return embedding
        except openai.APIStatusError as e:
            logging.warning("OPENAI: APIStatusError")
            logging.warning(e.status_code)
            logging.warning(e.response)
            logging.warning(e.message)
            raise e
        except openai.APIConnectionError as e:
            logging.warning("OPENAI: APIConnectionError")
            logging.warning(e.message)
            raise e
        except openai.APIError as e:
            logging.warning("OPENAI: APIError")
            logging.warning(e.message)
            raise e
        except Exception as e:
            logging.warning("OPENAI: Exception")
            logging.warning(e)
            raise e


class AzureOpenAIEmbeddingAda(AzureOpenAIEmbedding):
    def __init__(self, model: str = "text-embedding-ada-002") -> None:
        super().__init__(model)
