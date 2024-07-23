'''
Module for querying OpenAI's GPT-4o model to parse through data and extract pricing
'''

import openai
import web_scraper
import re

from constants import OPENAI_API_KEY, COST_PER_INPUT_TOKEN, COST_PER_OUTPUT_TOKEN, GPT_ENCODING, TREATMENTS
from log import log



class GPT:
    __slots__ = ('client')

    def __init__(self) -> None:
        self.client=openai.OpenAI(
            api_key=OPENAI_API_KEY,
        )

    def query_prices_per_minute(self, location: str) -> dict[str, float] | None:
        sources = set()

        for treatment in TREATMENTS:
            sources |= set(web_scraper.get_search_price_data(f'{treatment} "pricing" {location}'))

        all_sources = 'SOURCES:\n\n' + '\n\nEND OF SOURCE\n\n'.join(sources) + '\n\nEND OF SOURCES'

        tokens = self.get_tokens(all_sources)

        if tokens <= 25_000:
            prices: dict[str, float] = {}

            cost = 0

            for treatment in TREATMENTS:
                prompt = f'I am trying to get a price per minute estimate for {treatment} in {location}. Using the given sources, find the pricing and duration of sessions, and calculate the price per minute. If a session isn\'t listed as {treatment}, don\'t include it. Don\'t include any prices that are for systems, I only want services. Don\'t include any repeated data points. Use at most 20 options, but if there are less thats ok.\nIn your reply, tell me ONLY:\nlist of - prices per minute (session length, session cost)\nAverage: the average.'

                completion = self.client.chat.completions.create(
                    messages=[
                        {
                            'role': 'system',
                            'content': 'Help the user parse through the provided sources to find pricing information. You can use outside knowledge about the general costs of areas to help fill in potential gaps in the data. Don\'t use markdown formatting'
                        },
                        {
                            'role': 'user',
                            'content': all_sources
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    model='gpt-4o',
                    temperature=0.3,
                    n=1,
                    max_tokens=750
                )

                reply = str(completion.choices[0].message.content)
                tokens = completion.usage

                cost += tokens.prompt_tokens * COST_PER_INPUT_TOKEN       # type: ignore
                cost += tokens.completion_tokens * COST_PER_OUTPUT_TOKEN  # type: ignore

                log(reply + '\n\n', 'gpt_responses.txt')

                prices[treatment] = extract_pricing(reply)

            log(f'Query cost: ${cost:.3f}\n\n\n', 'gpt_responses.txt')

            return prices

        else:
            log(f'Too many tokens for request: {tokens}\n\n\n', 'gpt_responses.txt')

    def get_tokens(self, message: str) -> int:
        return len(GPT_ENCODING.encode(message))



def extract_pricing(reply: str) -> float:
    '''
    get the price per minute value out of a GPT reply.
    '''

    for line in reply.lower().splitlines():
        if 'average:' in line: # extract the average price
            ppm = re.findall(r"[-+]?(?:\d*\.*\d+)", line)

            if ppm:
                return float(ppm[0])

    # no pricing information available
    return -1.0

