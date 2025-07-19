# imports here
import json
import random
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import requests
import imghdr

from utils import loop_to_check


# code by pythonjar, not me
options = webdriver.EdgeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
options.add_experimental_option("prefs", prefs)


# get all the image urls from the page
def get_image_urls(page_url, driver: webdriver.Edge):
    page_id = page_url.split("/")[-2]
    driver.get(page_url)
    time.sleep(5)

    # anchors = retrieve_anchor_elements(driver, page_id)

    with open("anchors.txt", "r") as f:
        anchors = f.readlines()

    anchors = [a.strip() for a in anchors if a.strip()]

    image_urls = set()

    for a in anchors:
        start = time.time()
        driver.get(a)  # navigate to link
        img = loop_to_check(
            driver,
            EC.presence_of_element_located((By.TAG_NAME, "img")),
            timeout=6,
            message="Waiting for image to be present...",
        )

        image_url = img.get_attribute("src")
        image_urls.add(image_url)  # may change in future to img[?]

        date_element = loop_to_check(
            driver,
            EC.presence_of_element_located(
                (By.XPATH, '//div[./span[@class="xuxw1ft"]]/child::*[1]')
            ),
            timeout=6,
            message="Waiting for date element to be present...",
        )

        action = webdriver.ActionChains(driver)
        action.move_to_element(date_element).perform()

        time.sleep(1)  # wait for the link to be present

        link_element = loop_to_check(
            driver,
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[./span[@class="xuxw1ft"]]//a',
                )
            ),
            timeout=6,
            message="Waiting for post link to be present...",
        )

        post_url = link_element.get_attribute("href")

        with open("images.jsonl", "a") as f:
            f.write(json.dumps({"url": image_url, "post": post_url}) + "\n")

        time.sleep(
            (time.time() - start) + random.choice(range(5, 10))
        )  # wait for 20 seconds before next iteration

    print("Found " + str(len(image_urls)) + " urls to images")
    return list(image_urls)


def retrieve_anchor_elements(driver: webdriver.Edge, page_id):
    SCROLL_PAUSE_TIME = 3
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Create a file to store anchors
    if not os.path.exists("anchors.txt"):
        with open("anchors.txt", "w") as f:
            f.write("")

    while True:
        # Scroll down to bottom
        temp_anchors = driver.find_elements(By.TAG_NAME, "a")
        temp_anchors = [a.get_attribute("href") for a in temp_anchors]
        temp_anchors = [
            a
            for a in temp_anchors
            if str(a).startswith("https://www.facebook.com/photo") or "photo" in str(a)
        ]

        for a in temp_anchors:
            with open("anchors.txt", "r") as f:
                existing_anchors = f.readlines()
            existing_anchors = [x.strip() for x in existing_anchors]

            if a not in existing_anchors:
                with open("anchors.txt", "a") as f:
                    f.write(a.strip() + "\n")

        current_photo_containers = driver.find_elements(
            By.XPATH, '//div[@class="x1e56ztr"]/div[1]/div'
        )

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        waited_time = 0
        changed_number = 0
        while True:
            after_photo_containers = driver.find_elements(
                By.XPATH, '//div[@class="x1e56ztr"]/div[1]/div'
            )
            if len(after_photo_containers) == len(current_photo_containers):
                try:
                    driver.find_element(By.XPATH, '//div[@class="x1gslohp"]')
                    continue
                except Exception as e:
                    break
            elif len(after_photo_containers) > len(current_photo_containers):
                changed_number = len(after_photo_containers) - len(
                    current_photo_containers
                )
                break
            time.sleep(SCROLL_PAUSE_TIME)
            waited_time += SCROLL_PAUSE_TIME
            if waited_time > 300:  # 5 minutes
                print("Waited too long for new images, breaking...")
                break

        # Calculate new scroll height and compare with last scroll height
        if changed_number < 3:
            break
        else:
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    with open("anchors.txt", "r") as f:
        anchors = f.readlines()
    anchors = [a.strip() for a in anchors if a.strip()]

    print(f"Collected {len(anchors)}  anchor elements from the photos.")

    return anchors


# download the image given the url and basename
def download_image(url, basename):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError
    extension = imghdr.what(file=None, h=response.content)
    save_path = f"{basename}.{extension}"
    with open(save_path, "wb") as f:
        f.write(response.content)


def main(page_urls):
    driver = webdriver.Edge(options=options)

    # open the webpage
    driver.get("http://www.facebook.com")

    # target username
    username = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']"))
    )
    password = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']"))
    )

    # enter username and password
    username.clear()
    for letter in os.environ["username"]:
        time.sleep(0.1)
        username.send_keys(letter)
    password.clear()
    for letter in os.environ["password"]:
        time.sleep(0.1)
        password.send_keys(letter)

    # target the login button and click it
    # button = (
    #     WebDriverWait(driver, 2)
    #     .until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    #     .click()
    # )

    while True:
        try:
            _ = driver.find_element(By.XPATH, '//div[@aria-label="Tạo bài viết"]')
        except Exception as e:
            continue

        # We are logged in!
        print("Logged in!!")

        for page_url in page_urls:

            if "groups" in page_url:
                page_url = page_url + "/media/photos"
            else:
                page_url = page_url + "/photos"

            image_urls = get_image_urls(page_url, driver)

            path = os.getcwd()
            path = os.path.join(path, "Memes", page_url.split("/")[-2])

            if not os.path.exists(path):
                os.makedirs(path)

            counter = 1
            for image_url in image_urls:
                download_image(image_url, os.path.join(path, str(counter)))
                counter += 1

        driver.quit()


if __name__ == "__main__":
    os.environ["username"] = "gbao.scientist@gmail.com"
    os.environ["password"] = "giabao0120"

    urls = [
        "https://www.facebook.com/sudlokomteen",
    ]

    main(urls)
