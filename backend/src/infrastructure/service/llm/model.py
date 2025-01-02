from abc import abstractmethod
from typing import Any
import logging
import json

import openai
import tiktoken
import groq
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_fixed
import httpx
from groq import AsyncGroq

from .... import config


class BaseLLM:
    """
    BaseLLM is an abstract base class for Language Model classes.

    Attributes:
        None

    Methods:
        __call__: Abstract method that must be implemented by subclasses. It represents the main functionality of the Language Model.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


class AzureOpenAI(BaseLLM):
    def __init__(self, model: str = "gpt-4") -> None:
        self.model = model
        self.client = openai.AsyncAzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=model,
            api_key=config.AZURE_OPENAI_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
        )

    @retry(
        stop=(stop_after_delay(120) | stop_after_attempt(3)),
        wait=wait_fixed(1),
        retry_error_callback=lambda retry_state: None,
    )
    async def __call__(
        self,
        prompt: list[dict],
        stream: bool = True,
        temperature: float = 0,
        stop: list[str] = None,
    ):
        """
        Calls the Azure OpenAI language model to generate completions based on the given prompt.

        Args:
            prompt (list[dict]): A list of messages in the conversation prompt. Each message is represented as a dictionary with 'role' and 'content' keys.
            stream (bool, optional): If True, returns a generator that streams the response in chunks. If False, returns a single response. Defaults to True.

        Returns:
            If stream is True, a generator that yields the response chunks. If stream is False, a single response.

        Raises:
            openai.APIStatusError: If there is an API status error.
            openai.APIConnectionError: If there is an API connection error.
            openai.APIError: If there is an API error.
            Exception: If there is any other exception.

        Example:
            llm = AzureOpenAI()
            completions = await llm(
                [
                    {
                        "role": "user",
                        "content": "write a random paragraph for me in no more than 50 words.",
                    }
                ],
                stream=True,
            )
            async for chuck in completions:
                if chuck is not None:
                    print(chuck, end="", flush=True)
        """
        try:
            completions = await self.client.chat.completions.create(
                model=self.model,
                messages=prompt,
                temperature=0,
                stream=stream,
                stop=stop,
            )

            async def stream_response():
                async for chunk in completions:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

            def single_response():
                return completions.choices[0].message.content

            return stream_response() if stream else single_response()

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

    def compute_prompt_token_size(self, prompt: str):
        enc = tiktoken.encoding_for_model(self.model)
        return len(enc.encode(prompt))


class Groq(AzureOpenAI):
    def __init__(self, model: str) -> None:
        super().__init__(model)

        self.client = groq.AsyncGroq(
            api_key=config.GROQ_KEY,
        )
        self.model = model


class GroqMixtral(Groq):
    def __init__(self) -> None:
        super().__init__(model=config.GROQ_MIXTRAL_NAME)


class GroqLlama3_70B(Groq):
    def __init__(self) -> None:
        super().__init__(model=config.GROQ_LLAMA3_70b_name)


class GroqLlama3_8B(Groq):
    def __init__(self) -> None:
        super().__init__(model=config.GROQ_LLAMA3_8b_name)


class AzureOpenAIGPT4Turbo(AzureOpenAI):
    def __init__(self) -> None:
        super().__init__(model="gpt-4")


class AzureOpenAIGPT4O(AzureOpenAI):
    def __init__(self) -> None:
        super().__init__(model="gpt-4o")


class AzureOpenAIGPT35Turbo(AzureOpenAI):
    def __init__(self) -> None:
        super().__init__(model="gpt-35-turbo")


class GroqAI(BaseLLM):
    def __init__(self, model: str = "mixtral-8x7b-32768") -> None:
        self.model = model
        self.client = AsyncGroq(
            api_key=config.GROQ_KEY,
        )

    @retry(
        stop=(stop_after_delay(120) | stop_after_attempt(3)),
        wait=wait_fixed(1),
        retry_error_callback=lambda retry_state: None,
    )
    async def __call__(self, prompt: list[dict], stream: bool = True):
        """
        Calls the Azure OpenAI language model to generate completions based on the given prompt.

        Args:
            prompt (list[dict]): A list of messages in the conversation prompt. Each message is represented as a dictionary with 'role' and 'content' keys.
            stream (bool, optional): If True, returns a generator that streams the response in chunks. If False, returns a single response. Defaults to True.

        Returns:
            If stream is True, a generator that yields the response chunks. If stream is False, a single response.

        Raises:
            openai.APIStatusError: If there is an API status error.
            openai.APIConnectionError: If there is an API connection error.
            openai.APIError: If there is an API error.
            Exception: If there is any other exception.

        Example:
            llm = AzureOpenAI()
            completions = await llm(
                [
                    {
                        "role": "user",
                        "content": "write a random paragraph for me in no more than 50 words.",
                    }
                ],
                stream=True,
            )
            async for chuck in completions:
                if chuck is not None:
                    print(chuck, end="", flush=True)
        """
        try:
            completions = await self.client.chat.completions.create(
                model=self.model, messages=prompt, temperature=0, stream=stream
            )

            async def stream_response():
                async for chunk in completions:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

            def single_response():
                return completions.choices[0].message.content

            return stream_response() if stream else single_response()

        except openai.APIStatusError as e:
            logging.warning("OPENAI: APIStatusError")
            logging.warning(e.status_code)
            logging.warning(e.response)
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


class Ollama:
    def __init__(self) -> None:
        self.llm = httpx.AsyncClient(base_url="http://localhost:11434/", timeout=10)

    async def __call__(self, prompt, stream=True) -> Any:
        prompt = "\n".join(
            [f'{message.get("role")}:{message.get("content")}' for message in prompt]
        )
        data = json.dumps(
            {
                "model": "mistral:instruct",
                "prompt": prompt,
                "options": {"temperature": 0},
            }
        )

        params = {
            "method": "POST",
            "url": "api/generate",
            "data": data,
            "headers": {"Content-Type": "application/json"},
        }

        if stream:

            async def stream_response():
                async with self.llm.stream(**params) as response:
                    async for chunk in response.aiter_bytes():
                        yield json.loads(chunk.decode("utf-8")).get("response")

            return stream_response()
        else:
            r = await self.llm.request(**params)
            return "".join(
                [
                    json.loads(token).get("response")
                    for token in r.content.decode("utf-8").split("\n")
                    if token != ""
                ]
            )


async def main():
    llm = AzureOpenAI()
    completions = await llm(
        [
            {
                "role": "user",
                "content": "write a random paragraph for me in no more than 50 words.",
            }
        ],
        stream=True,
    )
    print(type(completions))
    async for chuck in completions:
        if chuck is not None:
            print(chuck, end="", flush=True)
