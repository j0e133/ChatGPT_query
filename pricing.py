'''
Module for getting the pricing information of treatments is different zipcodes and cities
'''

from queue import Queue
from threading import Thread, Lock

import database
from database import PricingData
from gpt import GPT
from treatments import Treatment
from zipcode import Zipcode



class PriceManager:
    __slots__ = ('gpt', 'database')

    def __init__(self) -> None:
        self.gpt = GPT()
        self.database = database.load()

    def get_saved_pricing(self, zipcode: Zipcode) -> PricingData:
        city = zipcode.city

        if city in self.database:
            return self.database[city]

        else:
            return {}

    def get_prices_per_minute(self, city: str, treatments: list[Treatment], update_database: bool) -> PricingData:
        '''
        Gets the prices per minute for each listed treatment and returns the result.

        Intended to run on a separate thread.
        '''

        # create threads for each treatment and a shared lock
        threads: list[Thread] = []

        queue: Queue[PricingData] = Queue()
        lock = Lock()

        for treatment in treatments:
            thread = Thread(target=self.price_worker, args=(city, treatment, update_database, queue, lock))

            thread.start()

            threads.append(thread)

        # wait for threads to finish
        for thread in threads:
            thread.join()

        # save database and put return value in queue
        database.save(self.database)

        prices: PricingData = {}

        while True:
            try:
                prices.update(queue.get(block=False))
            except:
                break

        return prices

    def price_worker(self, city: str, treatment: Treatment, update_database: bool, queue: Queue[PricingData], lock: Lock) -> None:
        '''
        Worker function for getting the price of a treatment

        Intended to run on a separate thread.
        '''

        if city not in self.database or treatment.name not in self.database[city] or update_database:
            ppm = round(self.gpt.query_treatment_pricing(city, treatment), 2)

            with lock:
                if city not in self.database:
                    self.database[city] = {}

                self.database[city][treatment.name] = ppm

        queue.put({treatment.name: self.database[city][treatment.name]})

