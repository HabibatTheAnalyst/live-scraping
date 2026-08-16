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
parsed_data = None

table_body_id = "ngx_equities_trading_statistics"
next_button_id = "latestdiclosuresEquities_next"  # from the paginate "Next" <a> id

def get_current_page_number(driver):
    # what page am I actually looking at
    try:
        current = driver.find_element(By.CSS_SELECTOR, "a.paginate_button.current")
        text = current.text.strip()
        return int(text) if text.isdigit() else None
    except Exception:
        return None

def is_next_disabled(driver):
    # adds a 'disabled' class to the Next button once on the last page
    try:
        next_btn = driver.find_element(By.ID, next_button_id)
    except Exception:
        return True
    classes = next_btn.get_attribute("class") or ""
    return "disabled" in classes

def click_next_and_wait(driver, expected_page, timeout=15):
    # click Next and wait until the 'current page' indicator actually reads expected_page
    # this is necessary because the Next button can be clicked before the page has actually changed
    next_btn = driver.find_element(By.ID, next_button_id)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
    try:
        next_btn.click()
    except Exception:
        # fall back to a JS click if something (sticky header/footer, overlay) is intercepting the real click
        driver.execute_script("arguments[0].click();", next_btn)

    WebDriverWait(driver, timeout).until(
        lambda d: get_current_page_number(d) == expected_page
    )

def paginate(driver, safety_cap=50):
    # Walk through every page of the table, collecting page_source after each one
    pages_html = []

    page_num = 1
    while True:
        actual_page = get_current_page_number(driver)
        print(f"capturing page {page_num} (site confirms current page = {actual_page})")
        if actual_page is not None and actual_page != page_num:
            print(f"  warning: expected page {page_num} but site shows page {actual_page}")
        pages_html.append(driver.page_source)

        if is_next_disabled(driver):
            print("Next button is disabled - this is the last page")
            break

        if page_num >= safety_cap:
            print(f"hit safety cap ({safety_cap} pages) - stopping as a precaution")
            break

        click_next_and_wait(driver, expected_page=page_num + 1)
        page_num += 1

    return pages_html

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
                lambda d: len(d.find_element(By.ID, table_body_id)
                              .find_elements(By.TAG_NAME, "tr")) > 0
            )
            print("successfuly fetched site data")

            pages_html = paginate(driver)
            return pages_html
        except (RequestException, TimeoutException) as e:
            print(f"attempt {attempts +1}, failed: {e}")
            time.sleep(delay)
        finally:
            if driver:
                driver.quit()
    print(f"all retries failed for {url}")
    return

def parse_site_data(pages_html):
    global parsed_data
    try:
        headers = None
        data = []

        for i, html in enumerate(pages_html, start=1):
            soup = BeautifulSoup(html, "html.parser")

            if headers is None:
                header_names = soup.find("thead").find_all("th")  # Extract headers once
                headers = [
                    header.get_text(strip=True)
                    for header in header_names
                ]

            body_data = soup.find("tbody", id=table_body_id).find_all("tr")  # Extract body data
            print(f"page {i}: extracted {len(body_data)} rows of data")
            for row in body_data:
                cols = row.find_all("td")
                values = [
                    col.get_text(strip=True)
                    for col in cols
                ]
                data.append(values)

        parsed_data = {
            "headers": headers,
            "data": data
        }
    except Exception as e:
        print(f"Error parsing site data: {e}")
        parsed_data = None

def save_to_csv(filename="financial_services_data.csv"):
    if not parsed_data:
        print("No data extracted")
        return
    df = pd.DataFrame(parsed_data["data"], columns=parsed_data["headers"])
    df.to_csv(filename, index=False)
    print(f"saved {len(df)} rows to {filename}")

def refresh_financial_data():
    pages_html = fetch_live_site(url)
    if pages_html:
        parse_site_data(pages_html)
        save_to_csv()
    else:
        print("html fetch unsuccessful")

if __name__ == "__main__":
    refresh_financial_data()