import os
import sys
from typing import Any

import tiktoken

from exceptions import retry_on_connection_error
from secret import * # sensitive information not included on github



# ui
FONT = 'Sylfaen'
DEFAULT_FONT = (FONT, 12)

BACKGROUND_COLOR = 'gray80'
TEXT_COLOR = 'black'
ELEMENT_COLOR = 'gray75'
ELEMENT_HOVER_COLOR = 'gray70'
ELEMENT_PRESS_COLOR = 'gray65'

LABEL_COLORS: dict[str, Any] = {
    'foreground': TEXT_COLOR,
    'background': BACKGROUND_COLOR
}

BUTTON_COLORS: dict[str, Any] = {
    'foreground': TEXT_COLOR,
    'activeforeground': TEXT_COLOR,
    'background': ELEMENT_COLOR,
    'activebackground': ELEMENT_PRESS_COLOR,
}

CHECKBOX_COLORS: dict[str, Any] = {
    'foreground': TEXT_COLOR,
    'background': BACKGROUND_COLOR,
    'activebackground': BACKGROUND_COLOR,
}

ENTRY_COLORS: dict[str, Any] = {
    'foreground': TEXT_COLOR,
    'background': ELEMENT_COLOR,
}


# directory paths
if getattr(sys, 'frozen', False): # If the application is run as an exe
    ROOT_DIR = os.path.dirname(sys.executable)

    DATA_DIR = os.path.join(ROOT_DIR, 'data')

else: # If the application is run as a script (the 'data' folder is in a 'dist' folder that PyInstaller creates)
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    DATA_DIR = os.path.join(ROOT_DIR, 'dist', 'data')


# search
SEARCH_KEYWORDS = {
    'price': 3,
    'min': 3,
    '$': 6,
    'package': 1,
    'sessions': 1,
}


# messages
SYSTEM_MESSAGE = {
    'role': 'system',
    'content': 'Help the user search through the sources they provide to find pricing information.'
}
PROMPT = '''
I am trying to get a price estimate for {} in {}.
Based on the sources I have provided, find the price and duration of different sessions.
If a session isn't listed as {}, don't include it.
Sources may have multiple sessions at different prices, so include all of them.
Try to get at least one sample from each source.
You can use your knowledge about the general cost of {} based on city size, and the size of {} to add samples to fill in potential gaps in the data.
Don't include any prices that are more than $10 per minute.
Give me at least 8, but less than 25 samples, and don't repeat any data points.
'''[1:-1].replace('\n', ' ')


# model info
MODEL_NAME = 'gpt-4o-2024-08-06'
MODEL_TEMPERATURE = 0.3


# token stuff
@retry_on_connection_error()
def get_4o_encoding() -> tiktoken.Encoding:
    return tiktoken.encoding_for_model('gpt-4o')

GPT_ENCODING = get_4o_encoding()

MAX_INPUT_TOKENS_PER_QUERY = 12_500
MAX_OUTPUT_TOKENS_PER_QUERY = 1_000

MAX_TOKENS_PER_MINUTE = 40_000

COST_PER_INPUT_TOKEN = 2.50 / 1_000_000
COST_PER_OUTPUT_TOKEN = 10.00 / 1_000_000
