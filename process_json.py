import json
import os


from tqdm import tqdm

from utils import download_image, remove_query_params


def download_images(
    file_name,
    start_index,
    end_index,
    save_index=0,
    save_path="Memes/sudlokomteen",
    group_alias=None,
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

        if "scontent.fsin" not in image_url:
            continue

        is_file_correct = False
        for alias in group_alias:
            if alias in post_url:
                is_file_correct = True
                break

        if not is_file_correct:
            continue

        post_url = remove_query_params(post_url)

        if post_url not in post_img:
            post_img[post_url] = []
        post_img[post_url].append(image_url)

    with open(f"{save_path}/post_with_one_image.jsonl", "w") as f:
        for post, images in tqdm(post_img.items(), desc="Download images..."):
            if len(images) == 1:
                f.write(json.dumps({"post": post, "url": images[0]}) + "\n")
                basename = f"image_{save_index}"
                try:
                    download_image(images[0], os.path.join(save_path, basename))
                    save_index += 1
                except Exception as e:
                    print(f"Error downloading {images[0]}: {e}")  # skip if any error occurs


start_index = 5378
end_index = -1
save_index = 0
file_name = "Memes/468871324329951/images.jsonl"
save_path = "Memes/468871324329951/images"
group_alias = ["468871324329951", "cotsonggenz"]
download_images(
    file_name,
    start_index,
    end_index,
    save_index,
    save_path,
    group_alias,
)
