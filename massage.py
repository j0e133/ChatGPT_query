'''
Module for getting the pricing information of massages using a specific website where you can input a latitude and longitude
'''

from statistics import median

import web_scraper
from zipcode import Zipcode



def get_massage_pricing(zipcode: Zipcode, durations: list[int], max_dist: float) -> dict[int, float]:
    '''
    Get the average price of a `duration` minute massage within `max_dist` miles of `zipcode`.
    
    Uses a specific website for higher accuracy.

    Doesn't work well for `duration <= 45`.
    '''

    url = f'https://www.massagebook.com/search/massage-therapy?latlng={zipcode.lat},{zipcode.long}'

    massage_data = web_scraper.get_website_data(url, {'min': 1, '$': 1, 'miles': 1}, 0)

    # extract the duration and price of each massage
    time_cost: dict[int, list[float]] = {}

    dist = time = cost = 0

    for line in massage_data.splitlines():
        if 'mile' in line:
            if time or cost: # reset if the order is messed up
                dist = time = cost = 0
                continue

            else:
                dist = float(line.strip('miles away '))

                if dist > max_dist:
                    dist = time = cost = 0
                    continue

        elif 'min' in line:
            if (not dist) or time or cost: # reset if the order is messed up
                dist = time = cost = 0
                continue

            else:
                time = int(line.strip('min '))

        elif '$' in line:
            if (not dist) or (not time) or cost: # reset if the order is messed up
                dist = time = cost = 0
                continue

            else:
                cost = float(line.strip('$ ').replace(',', ''))

        if dist and time and cost:
            if time not in time_cost:
                time_cost[time] = []

            time_cost[time].append(cost)

            dist = time = cost = 0

    samples: list[int] = []
    prices: list[float] = []

    # get the price for each massage duration
    for duration in durations:
        # get the price per minute of all massages within `variance` minutes of the specified duration
        ppms: list[float] = []
        variance = 5 * round(duration ** 0.5 / 5)

        for time in time_cost:
            if abs(time - duration) <= variance:
                ppms.extend(map(lambda i: i / time, time_cost[time]))

        if not ppms:
            continue

        # remove prices per minute that are less than half of or more than double the median
        med = median(ppms)
        no_outliers = list(filter(lambda x: 0.5 < abs(x / med) < 2, ppms))

        # calculate average
        sample_size = len(no_outliers)
        ppm = sum(no_outliers) / sample_size

        samples.append(sample_size)
        prices.append(ppm * duration)
    
    return {duration: price for duration, price in zip(durations, prices)}

