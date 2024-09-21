'''
Module for querying OpenAI's GPT-4o model to parse through data and extract pricing information.
'''

from typing import Sequence, Optional

import openai
from openai import RateLimitError
from openai.types.chat.parsed_chat_completion import ParsedChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel, Field

import web_scraper
from constants import *
from exceptions import retry_on_exception, retry_on_connection_error
from log import log
from treatments import Treatment



class Sample(BaseModel):
    provider: Optional[str] = Field(description='The company that provides the treatment. Can be either the name/number of the source or the name of the company in a source. Should be "GPT" if the treatment isn\'t from a source, but from general knowledge of prices in the area.')
    duration: float = Field(description='The length of the treatment in minutes.')
    cost: float = Field(description='The cost of the treatment.')
    package_count: int = Field(description='The number of treatments in a package. Should be 1 if the treatment isn\'t a package.')



class TreatmentPrices(BaseModel):
    treatment: str = Field(description='The name of the treatment.')
    samples: list[Sample] = Field(description='Samples of treatments from providers in the sources.')

    def get_pricing(self) -> float:
        '''
        Returns the average price per minute of the samples
        '''

        total = 0.0

        for treatment in self.samples:
            if treatment.duration and treatment.package_count:
                ppm = (treatment.cost / treatment.duration / treatment.package_count)

                if ppm <= 12.5:
                    total += ppm

        average = total / len(self.samples)

        return average



class GPT:
    __slots__ = ('client')

    def __init__(self) -> None:
        self.client=openai.OpenAI(api_key=OPENAI_API_KEY)

    @retry_on_exception(
        RateLimitError,
        max_retries=60,
        retry_after=5,
        retry_after_exponent=1.75
    )
    def get_completion(self, messages: Sequence[ChatCompletionMessageParam]) -> ParsedChatCompletion[TreatmentPrices]:
        completion = self.client.beta.chat.completions.parse(
            model = MODEL_NAME,
            messages = messages,
            response_format=TreatmentPrices,
            n = 1,
            temperature = MODEL_TEMPERATURE,
            max_tokens = MAX_OUTPUT_TOKENS_PER_QUERY,
        )

        return completion

    @retry_on_connection_error(default_value=0.0)
    def query_treatment_pricing(self, city: str, treatment: Treatment) -> float:
        keywords = SEARCH_KEYWORDS | treatment.keywords

        sources = web_scraper.get_search_data(f'{treatment.name} "pricing" {city}', keywords, 8)

        tokens = sum(map(token_count, sources))

        if tokens <= MAX_INPUT_TOKENS_PER_QUERY:
            source_messages = [{'role': 'user', 'content': f'## Source {i}:\n\n{source}'} for i, source in enumerate(sources)]

            messages = [SYSTEM_MESSAGE] + source_messages + [{'role': 'user', 'content': treatment.get_prompt(city)}]

            completion = self.get_completion(messages) # type: ignore

            reply = completion.choices[0].message.parsed

            if reply is None:
                return 0.0

            tokens = completion.usage
            query_cost = tokens.prompt_tokens * COST_PER_INPUT_TOKEN + tokens.completion_tokens * COST_PER_OUTPUT_TOKEN # type: ignore

            log(f'Query cost: ${query_cost:.3f}\n{reply.model_dump_json(indent=2)}\n\n', 'gpt_responses.txt')

            price_per_minute = reply.get_pricing()

            return price_per_minute

        return 0.0



def token_count(string: str) -> int:
    return len(GPT_ENCODING.encode(string))

