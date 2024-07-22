'''
Module for getting the pricing information of treatments is different zipcodes and cities
'''

import database

from queue import Queue
from gpt import GPT
from zipcode import Zipcode



class PriceManager:
    __slots__ = ('gpt', 'database')

    def __init__(self) -> None:
        self.gpt = GPT()
        self.database = database.load()

    def get_prices_per_minute(self, location: Zipcode | str, queue: Queue[dict[str, float] | None]) -> None:
        if isinstance(location, Zipcode):
            location = location.location

        if location in self.database:
            queue.put(self.database[location])

        else:
            gpt_estimate = self.gpt.query_prices_per_minute(location)

            if gpt_estimate is not None:
                self.database[location] = gpt_estimate

                database.save(self.database)

                queue.put(self.database[location])

            else:
                queue.put(None)

