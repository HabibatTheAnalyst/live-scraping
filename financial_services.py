import requests
import os
import time
# import pandas as pd
from dotenv import load_dotenv
# from bs4 import BeautifulSoup
from requests.exceptions import RequestException

load_dotenv()

url = os.getenv("SITE_URL")

def fetch_live_site(url, retries=3, delay=5):
    headers = {"user-agent": "mozilla/5.0"}
    for attempts in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print("successfuly fetched site data")
            return response.text
        except RequestException as e:
            print(f"attempt {attempts +1}, failed: {e}")
            time.sleep(delay)
    print(f"all retries failed for {url}")
    return None

html = fetch_live_site(url)
print(html)
