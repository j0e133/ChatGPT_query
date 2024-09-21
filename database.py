'''
Module for accessing and saving to the database file of saved search data
'''

import json
import os

from constants import DATA_DIR



DATABASE_PATH = os.path.join(DATA_DIR, 'search_save_data.json')

PricingData = dict[str, float]
Database = dict[str, PricingData]



def load() -> dict[str, PricingData]:
    with open(DATABASE_PATH) as f:
        data = json.loads(f.read())

    return data



def save(database: dict[str, PricingData]) -> None:
    with open(DATABASE_PATH, 'w') as f:
        f.write(json.dumps(database, indent=4))

