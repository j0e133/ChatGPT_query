import sys
import os
import tiktoken

# sensitive information not included on github
from secret import OPENAI_API_KEY, CUSTOM_SEARCH_API_KEY, CUSTOM_SEARCH_ENGINE_ID, USER_AGENT



if getattr(sys, 'frozen', False):
    # If the application is run as an exe
    ROOT_DIR = os.path.dirname(sys.executable)

    DATA_DIR = f'{ROOT_DIR}/data'

else:
    # If the application is run as a script (the 'data' folder is in a 'dist' folder that PyInstaller creates)
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    DATA_DIR = f'{ROOT_DIR}/dist/data'


COST_PER_INPUT_TOKEN = 5 / 1_000_000
COST_PER_OUTPUT_TOKEN = 15 / 1_000_000

GPT_ENCODING = tiktoken.encoding_for_model('gpt-4o')

TREATMENTS = [
    "Vibroacoustic Therapy",
    "Red Light Therapy",
    "PEMF",
    "Hyperbaric Oxygen Therapy",
    "Hocatt Treatment"
]
