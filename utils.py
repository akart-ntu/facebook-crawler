import time
from selenium.webdriver import Edge
from selenium.webdriver.support.wait import WebDriverWait


def loop_to_check(
    driver: Edge, condition, timeout=6, message="", exception_handler=None
):
    waited_time = 0
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
            if waited_time > timeout:
                print("Waited too long, reloading...")
                driver.refresh()
                waited_time = 0
    return web_element
