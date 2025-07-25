import time
from typing import Optional
from urllib.parse import urlparse, urlunparse
from selenium.webdriver import Edge
from selenium.webdriver.support.wait import WebDriverWait


def loop_to_check(
    driver: Edge,
    condition,
    timeout: Optional[int] = 6,
    message="",
    exception_handler=None,
):
    waited_time = 0
    web_element = None
    while True:
        start = time.time()
        try:
            web_element = WebDriverWait(driver, 3).until(condition)
            break
        except Exception as _:
            waited_time += time.time() - start
            if message:
                print(message)
            if exception_handler:
                exception_handler()
        finally:
            if timeout and waited_time > timeout:
                print("Waited too long, reloading...")
                driver.refresh()
                waited_time = 0
    return web_element


def remove_query_params(url: str) -> str:
    """
    Remove query parameters from the given URL.
    """
    parsed = urlparse(url)
    # urlunparse takes a tuple: (scheme, netloc, path, params, query, fragment)
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, "", parsed.fragment)
    )
