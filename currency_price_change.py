import requests
import os
import time
from dotenv import load_dotenv
from requests.exceptions import RequestException

load_dotenv()

url = os.getenv("SITE_URL")

def fetch_live_site(url, retries=3, delay=5):
    headers = {"User-Agent": "Mozilla/5.0"}

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print("successfully fetched data")
            return response.text

        except RequestException as e:
            print(f"attempt {attempt+1} failed: {e}")
            time.sleep(delay)

    print(f"all retries failed for {url}")
    return None
fetch_live_site(url)


if __name__ == "__main__":
    html = fetch_live_site(url)

    if html:
        print(html[:300])  # print first 300 characters