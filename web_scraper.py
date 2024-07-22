'''
Module conatining functions to scrape the web, including search and url parsing
'''

import requests

from constants import CUSTOM_SEARCH_API_KEY, CUSTOM_SEARCH_ENGINE_ID, USER_AGENT, GPT_ENCODING
from bs4 import BeautifulSoup
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

    log(query + '\n' + '\n'.join(urls) + '\n\n', 'searches.txt')

    return urls


def get_website_price_data(url: str, context: int = 7) -> str:
    '''
    Return the text contained in a website url.
    '''

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
    except:
        return ''

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        return extract_prices(soup.get_text(separator='\n', strip=True), context)

    else:
        log(f'Website access failed: error code {response.status_code} {response.reason}', 'searches.txt')

        return ''


def get_search_price_data(search_term: str, min_pages: int = 5, context: int = 7, max_tokens: int = 4_750) -> list[str]:
    '''
    Return `get_website_price_data()` for each url when `search_term` is searched.
    '''

    urls = search(search_term, 10)

    output = []
    tokens_left = max_tokens
    pages_left = min_pages
    page_token_limit = int(tokens_left * pages_left ** -0.75)

    for url in urls:
        price_data = get_website_price_data(url, context)

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
        if tokens_left == 0:
            break

    return output


def clean_text(text: str) -> str:
    '''
    Remove unnessecary whitespace, including empty indentations and leading and trailing spaces in each line.
    '''

    output = ''
    whitespace = False

    for line in text.splitlines():
        if line.isspace() or not line:
            if not whitespace:
                output += '\n'
                whitespace = True

        else:
            # remove all non-ascii characters from the line
            clean_line = ''

            for character in line:
                if character.isascii():
                    clean_line += character

            # clip line if it is over 100 tokens
            tokens = GPT_ENCODING.encode(clean_line)

            if len(tokens) > 100:
                clean_line = GPT_ENCODING.decode(tokens[:100])

            # add the line to the output
            output += clean_line
            output += '\n'
            whitespace = False

    return output


def extract_prices(text: str, context: int = 7) -> str:
    '''
    Remove unnessecary whitespace and then extract the lines with prices in them, along with `context` surrounding lines.
    '''

    lines = clean_text(text).splitlines()
    price_lines = set()

    # get lines with money values in them (costs)
    for i in range(len(lines)):
        if '$' in lines[i]:
            price_lines.add(i)

    # add the lines surrounding those with costs for context
    for i in price_lines.copy():
        for j in range(-context, context):
            price_lines.add(i + j)
    
    # get all of the lines
    output = '\n'.join(line for i, line in enumerate(lines) if i in price_lines)

    return output

