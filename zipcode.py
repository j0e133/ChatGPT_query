'''
Module for working with zip codes
'''

import zipcodes



class Zipcode:
    '''
    A class representing a US zip code, with information about city, state, and geographic coordinates (latitude and longitude)
    '''

    __slots__ = ('zipcode', 'data', 'location')

    def __init__(self, zipcode: int | str) -> None:
        self.zipcode = str(zipcode)

        if zipcodes.is_real(self.zipcode):
            self.data: dict[str, str] = zipcodes.matching(self.zipcode)[0]

            self.location = f'{self.data['city']}, {self.data['state']}'

        else:
            self.data = {}

            self.location = 'Invalid zip code'

