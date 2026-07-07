import requests
import os
import time
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
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

# def parse_site_data(html):
#     soup = BeautifulSoup(html, "html.parser")
#     items = []

#     # # target the needed section
#     # section = soup.select_one('section[data-test-id=" USD vs. All Currencies-cards-container"]')
#     # if not section:
#     #     print("section not found")
#     #     return items

#     rows = soup.select('tbody[data-test-id="table-body"] tr')

#     for row in rows:
#         cols = row.find_all("td")
#         if len(cols) < 6:
#             continue

#         name = cols[0].text.strip()
#         symbol = cols[1].text.strip()
#         rate = cols[2].text.strip()
#         change = cols[3].text.strip()
#         change_pct = cols[4].text.strip()
#         five_days = cols[5].text.strip()

#         items.append({
#             "name": name,
#             "symbol": symbol,
#             "rate": rate,
#             "change": change,
#             "change_pct": change_pct,
#             "five_days": five_days
#         })

#     return items

def parse_site_data(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []

    section = soup.find("section", attrs={"data-test-id": " USD vs. All Currencies-cards-container"})
    if not section:
        print("section not found")
        return items

    # rows = section.select('tbody[data-test-id="table-body"] tr')
    # print(f"rows found: {len(rows)}")

    rows = section.select('tbody[data-test-id="table-body"] tr')
    print(f"rows found: {len(rows)}")
    if rows:
        print(rows[0].prettify())

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue
        values = [col.get_text(strip=True) for col in cols]
        items.append({
            "name": values[0],
            "symbol": values[1],
            "rate": values[2],
            "change": values[3],
            "change_pct": values[4],
            "five_days": values[5]
        })
    return items

def save_to_csv(data, filename="output.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    html = fetch_live_site(url)

    if html:
        data = parse_site_data(html)

        if data:
            print(pd.DataFrame(data))
            save_to_csv(data, "currency_data.csv")
        else:
            print("No data extracted")



# import requests
# import os
# import time
# import pandas as pd
# from dotenv import load_dotenv
# from bs4 import BeautifulSoup
# from requests.exceptions import RequestException

# load_dotenv()
# url = os.getenv("SITE_URL")

# def fetch_live_site(url, retries=3, delay=5):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     for attempt in range(retries):
#         try:
#             response = requests.get(url, headers=headers, timeout=10)
#             response.raise_for_status()
#             print("successfully fetched data")
#             return response.text
#         except RequestException as e:
#             print(f"attempt {attempt+1} failed: {e}")
#             time.sleep(delay)
#     print(f"all retries failed for {url}")
#     return None

# def parse_site_data(html):
#     soup = BeautifulSoup(html, "html.parser")
#     sections = soup.find_all("section")
#     print(f"Total sections found: {len(sections)}")
#     for i, sec in enumerate(sections, 1):
#         tid = sec.get("data-test-id")
#         print(f"\nSection {i}: {repr(tid)}")
#     return []  # temporary, just debugging for now

# def save_to_csv(data, filename="output.csv"):
#     df = pd.DataFrame(data)
#     df.to_csv(filename, index=False)

# if __name__ == "__main__":
#     html = fetch_live_site(url)
#     if html:
#         data = parse_site_data(html)
#         if data:
#             print(pd.DataFrame(data))
#             save_to_csv(data, "currency_data.csv")
#         else:
#             print("No data extracted")