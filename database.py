'''
Module for accessing and saving to the database file of saved search data
'''

import json

from constants import DATA_DIR



DATABASE_PATH = f'{DATA_DIR}/search_save_data.json'

Database = dict[str, dict[str, float]]



def load() -> Database:
    with open(DATABASE_PATH) as f:
        return json.loads(f.read())


def save(database: Database) -> None:
    with open(DATABASE_PATH, 'w') as f:
        f.write(json.dumps(database, indent=4))

