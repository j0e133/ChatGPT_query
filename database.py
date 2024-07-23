'''
Module for accessing and saving to the database file of saved search data
'''

import json

from constants import DATA_DIR



DATABASE_PATH = f'{DATA_DIR}/search_save_data.json'



def load() -> dict[str, dict[str, float]]:
    with open(DATABASE_PATH) as f:
        return json.loads(f.read())


def save(database: dict[str, dict[str, float]]) -> None:
    with open(DATABASE_PATH, 'w') as f:
        f.write(json.dumps(database, indent=4))

