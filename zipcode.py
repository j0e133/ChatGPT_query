'''
Module for working with zip codes
'''

from statistics import median
import re

import zipcodes



class Zipcode:
    '''
    A class representing a US zip code, with information about city, state, and geographic coordinates (latitude and longitude)
    '''

    __slots__ = ('zipcode', 'is_real', 'data', 'city', 'lat', 'long')

    def __init__(self, zipcode: int | str) -> None:
        self.zipcode = str(zipcode)
        self.is_real = zipcodes.is_real(self.zipcode)

        if self.is_real:
            self.data: dict[str, str] = zipcodes.matching(self.zipcode)[0]

            self.city = f'{self.data['city']}, {self.data['state']}'

            self.lat: float = self.data['lat']   # type: ignore
            self.long: float = self.data['long'] # type: ignore

        else:
            self.data = {}

            self.city = 'Invalid zip code'

            self.lat = 0.0
            self.long = 0.0

    @classmethod
    def from_city(cls, city: str) -> 'Zipcode':
        city, state = city.split(', ')

        city_zipcodes = zipcodes.filter_by(city=city, state=state)

        lats = tuple(float(zipcode['lat']) for zipcode in city_zipcodes)
        longs = tuple(float(zipcode['long']) for zipcode in city_zipcodes)

        center_lat = median(lats)
        center_long = median(longs)

        zipcode_dict = min(city_zipcodes, key=lambda zipcode: ((float(zipcode['lat']) - center_lat) ** 2 + (float(zipcode['long']) - center_long) ** 2) ** 0.5)

        zipcode = Zipcode(zipcode_dict['zip_code'])

        return zipcode

    @staticmethod
    def is_city(string: str) -> bool:
        regex = r'^[A-Za-z]+(?:[ -][A-Za-z]+)*, [A-Z]{2}$'

        return bool(re.match(regex, string))

