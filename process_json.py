import json
import os

import requests
import imghdr


def download_image(url, basename):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError
    extension = imghdr.what(file=None, h=response.content)
    save_path = f"{basename}.{extension}"
    with open(save_path, "wb") as f:
        f.write(response.content)


with open("images.jsonl", "r") as f:
    content = f.readlines()

post_img = {}


for lines in content:
    data = json.loads(lines)
    image_url = data.get("url")
    post_url = data.get("post")

    if post_url not in post_img:
        post_img[post_url] = []
    post_img[post_url].append(image_url)

with open("post_with_one_image.jsonl", "w") as f:
    counter = 0
    for post, images in post_img.items():
        if len(images) == 1:
            f.write(json.dumps({"post": post, "url": images[0]}) + "\n")
            basename = f"image_{counter}"
            download_image(images[0], os.path.join("Memes", "sudlokomteen", basename))
            counter += 1
