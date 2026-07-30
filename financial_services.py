# import requests
import os
import time
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

load_dotenv()

url = os.getenv("SITE_URL")

def fetch_live_site(url, retries=3, delay=5):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=mozilla/5.0")

    for attempts in range(retries):
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            # wait until at least one <tr> has been injected into the tbody
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_element(By.ID, "ngx_equities_trading_statistics")
                              .find_elements(By.TAG_NAME, "tr")) > 0
            )
            print("successfuly fetched site data")
            return driver.page_source
        except (RequestException, TimeoutException) as e:
            print(f"attempt {attempts +1}, failed: {e}")
            time.sleep(delay)
        finally:
            if driver:
                driver.quit()
    print(f"all retries failed for {url}")
    return

def parse_site_data(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        header_names = soup.find("thead").find_all("th") # Extract headers
        headers = [
            header.get_text(strip=True)
            for header in header_names
        ]

        body_data = soup.find("tbody", id="ngx_equities_trading_statistics").find_all("tr") # Extract body data
        data = []
        print(f"Extracted {len(body_data)} rows of data")
        for row in body_data:
            cols = row.find_all("td")
            values = [
                col.get_text(strip=True)
                for col in cols
            ]
            data.append(values)
        return {
            "headers": headers,
            "data": data
        }

    except Exception as e:
        print(f"Error parsing site data: {e}")
        return None

def save_to_csv(data, filename="output.csv", headers=None):
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(filename, index=False)
    print(f"saved {len(df)} rows to {filename}")

def main():
    html = fetch_live_site(url)
    if html:
        parsed_data = parse_site_data(html)
        if parsed_data:
            # print(parsed_data["headers"])
            # print(parsed_data["data"])
            save_to_csv(parsed_data["data"], "financial_services_data.csv", parsed_data["headers"])
        else:
            print("No data extracted")
    else:
        print("Failed to fetch site data")

if __name__ == "__main__":
    main()