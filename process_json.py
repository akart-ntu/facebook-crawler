import json
import os

import requests
import imghdr

from tqdm import tqdm


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


def download_images(
    file_name,
    start_index,
    end_index,
    save_index=0,
    save_path="Memes/sudlokomteen",
):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    with open(file_name, "r") as f:
        content = f.readlines()

    post_img = {}

    for lines in tqdm(
        content[start_index:end_index], desc="Extract single image posts..."
    ):
        data = json.loads(lines)
        image_url = data.get("url")
        post_url = data.get("post")

        if post_url not in post_img:
            post_img[post_url] = []
        post_img[post_url].append(image_url)

    with open(f"{save_path}/post_with_one_image.jsonl", "w") as f:
        for post, images in tqdm(post_img.items(), desc="Download images..."):
            if len(images) == 1:
                f.write(json.dumps({"post": post, "url": images[0]}) + "\n")
                basename = f"image_{save_index}"
                download_image(images[0], os.path.join(save_path, basename))
                save_index += 1


start_index = 0
end_index = -1
save_index = 0
file_name = "Memes/1840261382820816/images.jsonl"
save_path = "Memes/1840261382820816/1840261382820816_1"
download_images(file_name, start_index, end_index, save_index, save_path)
