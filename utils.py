import time
from typing import Optional
from urllib.parse import urlparse, urlunparse
import requests
from selenium.webdriver import Edge
from selenium.webdriver.support.wait import WebDriverWait
import imghdr
import os


def download_image(url, basename):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError
    if ".jpg" in url:
        extension = "jpg"
    elif ".png" in url:
        extension = "png"
    else:
        extension = imghdr.what(file=None, h=response.content)
    save_path = f"{basename}.{extension}"
    with open(save_path, "wb") as f:
        f.write(response.content)


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


def reindex_images(image_dir: str, save_dir: str) -> None:
    files = os.listdir(image_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    index = 1
    for filename in files:
        full_path = os.path.join(image_dir, filename)
        if os.path.isfile(full_path) and imghdr.what(full_path):
            _, ext = os.path.splitext(filename)
            new_filename = f"image_{index}{ext}"
            new_path = os.path.join(save_dir, new_filename)
            os.rename(full_path, new_path)
            index += 1
