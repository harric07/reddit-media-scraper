# REDDIT MEDIA SCRAPER


import praw
import requests
from datetime import datetime
import os
import hashlib 
from PIL import Image
import json
import io

def scrape_reddit(page_name, download_limit):
    image_types = {"jpg", "bmp", "gif", "png", "tiff"}
    video_types = {"mp4"}
    reddit = praw.Reddit(client_id = "YOUR_CLIENT_ID",
                            client_secret = "YOUR_CLIENT_SECRET",
                            user_agent = "bot_v_0.0.0") # replace YOUR_CLIENT_ID and YOUR_CLIENT_SECRET with your own.
    page = reddit.subreddit(page_name)
    submissions = page.top(limit = download_limit )
    hashes = dict()
    current_directory = os.getcwd()
    sub_directory = f"{page_name}"
    new_directory = current_directory + '//' + sub_directory + '//'
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
        print("Created directory " + new_directory)
    else:
        try:
            hashes = json.load(open(new_directory + "hashes.txt"))
        except(FileNotFoundError):
            pass
    for i in submissions:
        if hasattr(i, "media_metadata") and i.media_metadata is not None:
            urls = []
            for item in i.media_metadata.items():
                urls.append(item[1]['p'][0]['u'].split("?")[0].replace("preview", "i"))
        elif hasattr(i, "preview") and "reddit_video_preview" in i.preview:
            urls = [i.preview["reddit_video_preview"]["fallback_url"]]
        else:
            urls = [i.url]
        for url in urls:
            if url in hashes.values():
                print(url + " is duplicate")
                continue
            date_created = i.created_utc
            date_time = datetime.utcfromtimestamp(date_created).strftime('%Y-%m-%d %H:%M:%S')
            file_type = url.split(".")[-1]
            if file_type in image_types:
                r = requests.get(url)
                md5_hash = hashlib.md5()
                image_data = Image.open(io.BytesIO(r.content)).tobytes()
                md5_hash.update(image_data)
                digest = md5_hash.hexdigest()
                if digest in hashes:
                    print(url + " is duplicate")
                    continue
                hashes[digest] = url
                file_name = new_directory + digest + "_" + date_time + "." + file_type
                with open(file_name, 'wb') as f:
                    f.write(r.content)
                    print(f"Downloaded: {url} as {digest}_{date_time}.{file_type}")
            elif file_type in video_types:
                r = requests.get(url)
                md5_hash = hashlib.md5()
                md5_hash.update(r.content)
                digest = md5_hash.hexdigest()
                if digest in hashes:
                    print(url + " is duplicate")
                    continue
                hashes[digest] = url
                file_name = new_directory + digest + "_" + date_time + "." + file_type
                with open(file_name, 'wb') as f:
                    f.write(r.content)
                    print(f"Downloaded: {url} as {digest}_{date_time}.{file_type}")
        json.dump(hashes, open(new_directory + "hashes.txt", "w"))

    


if __name__ == "__main__":
    reddit_sub_to_scrape = input("Enter the subreddit to scrape: ")
    number_of_posts_to_scrape = int(input("Enter the number of posts to scrape: "))
    print(f"Scraping '{reddit_sub_to_scrape}' for '{number_of_posts_to_scrape}' posts")
    scrape_reddit(reddit_sub_to_scrape, number_of_posts_to_scrape)
    print("Finished scraping, check the directory for the files")