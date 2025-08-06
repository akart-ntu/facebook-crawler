# imports here
import json
import random
from urllib.parse import parse_qs, urlparse
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
from tqdm import tqdm
from utils import loop_to_check
from seleniumbase import get_driver


# code by pythonjar, not me
options = webdriver.Firefox()


def get_object_id_from_url(url: str):
    url_components = url.replace("https://www.facebook.com/", "").split("/")
    if url_components[0] == "groups":
        return url_components[1]
    return url_components[0]


# get all the image urls from the page
def get_image_urls(page_url, driver: webdriver.Firefox):
    page_id = get_object_id_from_url(page_url)
    os.makedirs("Memes/" + page_id, exist_ok=True)

    base_path = os.path.join("Memes", page_id)
    jsonl_path = os.path.join(base_path, "images.jsonl")
    anchors_path = os.path.join(base_path, "anchors.txt")
    crawled_path = os.path.join(base_path, "crawled.txt")
    if not os.path.exists(crawled_path):
        open(crawled_path, "w").close()
    driver.get(page_url)
    time.sleep(5)

    if os.path.exists(anchors_path):
        with open(anchors_path, "r") as f:
            anchors = f.readlines()
    else:
        anchors = retrieve_anchor_elements(driver, anchors_path)

    anchors = [a.strip().replace("/?type=3", "") for a in anchors if a.strip()]
    image_urls = set()

    for a in tqdm(anchors, desc="Getting image URLs from anchors..."):
        a = a.replace("/?type=3", "").strip()
        parsed_url = urlparse(a)
        query_params = parse_qs(parsed_url.query)
        if "fbid" in query_params:
            fbid = query_params["fbid"][0]
        else:
            # if fbid is not in query params, extract it from the path
            fbid = a.split("/")[-1]
            if fbid.isdigit():
                fbid = fbid.strip()
            else:
                print(f"Invalid fbid in URL: {a}")
                continue
        # driver.get(f"https://www.facebook.com/photo/?fbid={fbid}")  # navigate to link
        # driver.get(a)
        driver.get(f"https://www.facebook.com/photo.php?fbid={fbid}")
        while True:

            def check_link_valid():
                driver.find_element(By.XPATH, '//span[contains(text(), "tiếc")]')
                raise ValueError("Post invalid or rate limit exceeded.")

            try:
                img = loop_to_check(
                    driver,
                    EC.presence_of_element_located((By.TAG_NAME, "img")),
                    timeout=6,
                    exception_handler=check_link_valid,
                    message="Waiting for image to be present...",
                )
                if not img:
                    continue
            except ValueError as e:
                break

            image_url = img.get_attribute("src")
            image_urls.add(image_url)  # may change in future to img[?]

            date_element = loop_to_check(
                driver,
                EC.presence_of_element_located(
                    (By.XPATH, '//div[./span[@class="xuxw1ft"]]//a')
                ),
                timeout=6,
                message="Waiting for date element to be present...",
            )

            if not date_element:
                continue

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
            if not link_element:
                continue

            # get the original post URL

            try:
                view_post = driver.find_element(
                    By.XPATH, '//a[contains(@href,"Xem bài viết")]'
                )
            except Exception as e:
                view_post = None

            if view_post:
                post_url = view_post.get_attribute("href")
            else:
                post_url = link_element.get_attribute("href")

            if "post" not in post_url:
                try:
                    post_link_element = driver.find_element(
                        By.XPATH, '//a[contains(@href,"post")]'
                    )
                    post_url = post_link_element.get_attribute("href")
                except Exception as e:
                    # if the found URL is a photo URL
                    # and there is no post link (showing that it belongs to a post),
                    # we may neglect it and use the original URL
                    pass

            with open(jsonl_path, "a") as f:
                f.write(json.dumps({"url": image_url, "post": post_url}) + "\n")

            time.sleep(
                random.choice(range(5, 15))
            )  # wait for 20 seconds before next iteration

            break

        with open(crawled_path, "a") as f:
            f.write(a.strip() + "\n")
    print("Found " + str(len(image_urls)) + " urls to images")
    return list(image_urls)


def retrieve_anchor_elements(driver: webdriver.Firefox, save_path="anchors.txt"):
    SCROLL_PAUSE_TIME = 3
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Create a file to store anchors
    if not os.path.exists(save_path):
        open(save_path, "x").close()

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
            with open(save_path, "r") as f:
                existing_anchors = f.readlines()
            existing_anchors = [x.strip() for x in existing_anchors]

            if a not in existing_anchors:
                with open(save_path, "a") as f:
                    f.write(a.strip() + "\n")

        current_photo_containers = driver.find_elements(
            By.XPATH, '//div[@class="x1e56ztr"]/div[1]/div'
        )

        if len(current_photo_containers) >= 9800:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        waited_time = 0
        while True:
            time.sleep(SCROLL_PAUSE_TIME)
            after_photo_containers = driver.find_elements(
                By.XPATH, '//div[@class="x1e56ztr"]/div[1]/div'
            )
            if len(after_photo_containers) == len(current_photo_containers):
                try:
                    driver.find_element(By.XPATH, '//div[@class="x1a2a7pz"]')
                    continue
                except Exception as e:
                    break
            elif len(after_photo_containers) > len(current_photo_containers):
                break
            waited_time += SCROLL_PAUSE_TIME
            if waited_time > 120:
                print("Waited too long for new images, breaking...")
                break

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    with open(save_path, "r") as f:
        anchors = f.readlines()
    anchors = [a.strip() for a in anchors if a.strip()]

    print(f"Collected {len(anchors)}  anchor elements from the photos.")

    return anchors


def main(page_urls):
    driver = get_driver("firefox")

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

    while True:
        try:
            _ = driver.find_element(By.XPATH, '//div[@aria-label="Tạo bài viết"]')
        except Exception as e:
            continue

        # We are logged in!
        print("Logged in!!")

        for page_url in page_urls:

            get_image_urls(page_url, driver)

        driver.quit()
        break


if __name__ == "__main__":
    os.environ["username"] = "giabao.cao.ntu@gmail.com"
    os.environ["password"] = ""
    # quanhust03@gmail.com
    # thapcam2trung

    urls = [
        "https://www.facebook.com/groups/468871324329951/media/photos"
    ]

    main(urls)
