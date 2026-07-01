import requests
import time
from requests.exceptions import RequestException

def load_config():
    read configuration file
    return config object


def fetch_live_site(url, retries=3, delay=5):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text

        except RequestException as e:
            print(f"[WARNING] Attempt {attempt+1} failed: {e}")
            time.sleep(delay)

    print(f"[ERROR] All retries failed for {url}")
    return None

def parse_site_data(raw_html):
    find the needed tables/cards/text from the page
    extract fields such as:
        - title
        - price/value/status
        - timestamp
        - source_url

    return extracted records

def clean_data(records):
    remove empty values
    fix text spacing
    convert numbers to correct format
    add scrape_time
    return cleaned records

def is_new_or_updated(data):
    compare current data with last saved version

    if data changed:
        return True
    else:
        return False

def send_to_kafka(producer, topic, data):
    convert data to JSON
    publish JSON message to Kafka topic
    log success

def kafka_consumer():
    consumer = connect_to_kafka(topic)

    for message in consumer:
        data = read_message(message)

        validated_data = validate_data(data)

        if validated_data is valid:
            save_to_database(validated_data)
        else:
            log bad data

def save_to_database(data):
    connect to database
    insert new record
    or update existing record if it already exists


def main():
    config = load_config()

    producer = create_kafka_producer(config.kafka_broker)

    while True:
        raw_html = fetch_live_site(config.site_url)

        if raw_html is not empty:
            extracted_data = parse_site_data(raw_html)

            cleaned_data = clean_data(extracted_data)

            if is_new_or_updated(cleaned_data):
                send_to_kafka(
                    producer,
                    topic=config.kafka_topic,
                    data=cleaned_data
                )

        wait(60 seconds)
def run_kafka_consumer():

def run_kafka_consumer():
    create_kafka_consumer()
    kafka_consumer()

if __name__ == "__main__":
    main()
    run_kafka_consumer()
