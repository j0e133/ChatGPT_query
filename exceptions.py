'''
Module containing decorators for handling exceptions and retrying functions.
'''


import time
from functools import partial
from tkinter import messagebox
from typing import Any, Callable, Optional, Type

import requests.exceptions



RetryPrompt = tuple[str, str]



def retry_on_exception(
        *exception_types: Type[Exception],
        max_retries: int = 1,
        retry_after: float = 0.0,
        retry_after_exponent: float = 1.0,
        default_value: Any = None,
        retry_prompt: Optional[RetryPrompt] = None,
        terminal_prompt: Optional[RetryPrompt] = None,
    ):

    '''
    Retries a function when it raises and error of type `exception_types`.

    Retries the function `max_retries` times.

    It will wait `retry_after` seconds to try again. `retry_after` is multiplied by `retry_after_exponent` each time it retries.

    If `default_value` is specified, it will return that value if it runs out of retries. Raises the final exception otherwise.

    If `retry_prompt` is specified, it will open a tkinter "retry or cancel" messagebox with each retry with the title and message being the two items of the tuple.

    If `terminal_prompt` is specified, it will open a tkinter "ok" messagebox when it runs out of retries with the title and message being the two items of the tuple.
    '''

    if retry_prompt is not None:
        window = messagebox.Message(
            icon='error',
            type='retrycancel',
            title=retry_prompt[0],
            message=retry_prompt[1]
        )

    if terminal_prompt:
        terminal_window = messagebox.Message(
            icon='error',
            type='ok',
            title=terminal_prompt[0],
            message=terminal_prompt[1]
        )

    def decorator(func: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exception_types as exception:
                    if attempt == max_retries:
                        if terminal_prompt:
                            terminal_window.show()

                        if default_value is not None:
                            return default_value

                        raise exception

                    elif retry_prompt is not None:
                        match window.show():
                            case 'retry':
                                pass
                            case 'cancel':
                                if default_value is not None:
                                    return default_value

                                raise exception

                    time.sleep(retry_after * retry_after_exponent ** attempt)

        return wrapper

    return decorator



def retry_on_connection_error(
        max_retries: int = 1,
        default_value: Any = None,
    ) -> Callable: # type: ignore

    '''
    Retries a function when it raises a requests connection or timeout error.

    Retries the function `max_retries` times.

    If `default_value` is specified, it will return that value if it runs out of retries. Raises the final exception otherwise.
    '''

    pass

retry_on_connection_error = partial(
    retry_on_exception,
    requests.exceptions.ConnectionError, requests.exceptions.Timeout,
    retry_prompt=(
        'Connection Error',
        'There was an error when trying to connect to the internet.\nPlease check your internet and try again.'
    ),
    terminal_prompt=(
        'Connection Failed',
        'Operation Cancelled.\nFailed when trying to connect to the internet.\nPlease check your internet and try again.'
    ),
) # type: ignore

