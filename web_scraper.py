'''
Module conatining functions to scrape the web, including search and url parsing
'''

from collections import deque

from bs4 import BeautifulSoup
import requests

from constants import *
from log import log



HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.9'
}



def search(query: str, num_urls: int, page: int = 1) -> list[str]:
    '''
    Searches google for `query` and returns `num_urls` urls.

    Uses Google's Custom Search Engine.
    '''

    url = 'https://www.googleapis.com/customsearch/v1'
    base_params = {
        'key': CUSTOM_SEARCH_API_KEY,
        'cx': CUSTOM_SEARCH_ENGINE_ID,
        'q': query,
    }

    urls = []

    while len(urls) < num_urls:
        params = base_params | {
            'num': min(10, num_urls - len(urls)),
            'start': page
        }

        response = requests.get(url, params=params, headers=HEADERS)

        if response.status_code == 200:
            results = response.json()
            items = [item['link'] for item in results.get('items', [])]
            urls.extend(items)

            page += len(items)

            if not items:
                break

        else:
            log(f'Search failed: error code {response.status_code} {response.reason}', 'searches.txt')

            return []

    log(f'{query}\n - {'\n - '.join(urls)}\n\n', 'searches.txt')

    return urls



def get_search_data(search_term: str, keywords: dict[str, int], min_pages: int) -> list[str]:
    '''
    Return `get_website_price_data()` for each url when `search_term` is searched.
    '''

    urls = search(search_term, 10)

    output = []
    tokens_left = MAX_INPUT_TOKENS_PER_QUERY - 250
    pages_left = min_pages
    page_token_limit = int(tokens_left * pages_left ** -0.75)

    for url in urls:
        price_data = get_website_data(url, keywords, 1)

        token_ids = GPT_ENCODING.encode(price_data)
        tokens = len(token_ids)

        # skip if there are no tokens
        if tokens == 0:
            continue

        # clamp the tokens if there are too many
        if tokens > page_token_limit:
            price_data = GPT_ENCODING.decode(token_ids[:page_token_limit])

        # add the source
        output.append(price_data)

        tokens_left -= min(tokens, page_token_limit)
        pages_left = max(1, pages_left - 1)
        page_token_limit = int(tokens_left * pages_left ** -0.75)

        # end if max_tokens is reached
        if tokens_left <= 0:
            break

    return output



def get_website_data(url: str, keywords: dict[str, int], duplicate_dist: int) -> str:
    '''
    Return the text contained in a website url.
    '''

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
    except:
        return ''

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        return extract_keywords(soup.get_text(separator='\n', strip=True), keywords, duplicate_dist)

    else:
        log(f'Website access failed: error code {response.status_code} {response.reason}', 'searches.txt')

        return ''



def extract_keywords(text: str, keywords: dict[str, int], duplicate_dist: int) -> str:
    '''
    Remove unnessecary whitespace and then extract the lines with `strings` keys in them, along with `strings` values surrounding lines.
    '''

    # lowercase all of the strings for comparison
    strings = {string.lower(): context for string, context in keywords.items()}

    lines = clean_text(text, duplicate_dist).splitlines(keepends=True)
    line_indices = set()
    output = ''

    # get lines with money values in them (costs)
    for i, line in enumerate(lines):
        line_compare = line.lower()
        j = 0

        # get the maximum context size to check
        for string, context in strings.items():
            j = max(j, context * (string in line_compare))

        # add the lines and context
        if j:
            line_indices.update(range(i - j, i + j + 1))

        if i in line_indices:
            output += line

    return output



def clean_text(text: str, duplicate_dist: int) -> str:
    '''
    Remove unnessecary whitespace, including empty indentations and leading and trailing spaces in each line.

    Also removes duplicate lines within `duplicate_lines` lines of the first one seen.
    '''

    output = ''
    lines: deque[str] = deque(maxlen=duplicate_dist)

    for line in text.splitlines(keepends=True):
        if line and not line.isspace():
            # remove all non-ascii characters from the line
            ascii_line = ''.join(filter(str.isascii, line))

            # clip line if it is over 100 tokens
            tokens = GPT_ENCODING.encode(ascii_line)

            if len(tokens) > 100:
                ascii_line = GPT_ENCODING.decode(tokens[:100])

            lowercase_line = ascii_line.lower()

            # skip if it is a duplicate
            if lowercase_line not in lines:
                output += ascii_line

                lines.append(lowercase_line)

    return output

