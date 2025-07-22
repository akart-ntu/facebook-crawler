# Facebook scraper without API limit

## Installtation

- Python version: 3.9+

Run

```bash
pip install -r requirements.txt
```

## Variables

In the `fb_crawler.py`, under `if __name__ == "__main__":`, set:

```python
os.environ["username"] = "[Facebook_account]"
urls = ["list of URLs pointing to the photo folder of the groups"
]
# For example:
# https://www.facebook.com/groups/2223334821036319/media/photos
```

## Run the crawler

```bash
python fb_crawler.py
```

## Workflow

1. The crawler will create an `anchors.txt` file under the `Memes/<GROUP_ID>` folder. This file contains post link containing that image
2. Next the crawler will iterate through all the anchors and file the original post URL, and get the link to the image with original size. The links found will be saved to a file `image.jsonl` under the same folder.
3. After finish running, use the `process_json.py` to download the image. To run the module, you will need to set the following variables inside that module to the path of `image.jsonl` and the directory where you want to save the downloaded images:
    ```python
    file_name = "Memes/Choptalokyurueai/images.jsonl"
    save_path = "Memes/Choptalokyurueai/choptalokyurueai_2"
    ```
