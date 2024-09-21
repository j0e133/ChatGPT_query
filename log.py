'''
Module for logging.
'''

import os

from constants import DATA_DIR



LOG_DIR = os.path.join(DATA_DIR, 'logs')



def log(message: str, file: str) -> None:
    '''
    For logging stuff incase of error or testing.
    '''

    with open(os.path.join(LOG_DIR, file), 'a') as f:
        f.write(message)

