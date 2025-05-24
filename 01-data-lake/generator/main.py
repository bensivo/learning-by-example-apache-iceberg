import datetime
import uuid
import io
import json
import random
from faker import Faker
from minio import Minio

MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "my-access-key"
MINIO_SECRET_KEY = "my-secret-key"
BUCKET_NAME = "raw"


def push_events_to_minio(events, bucket, filepath):
    """
    Push a list of dict events to MinIO in the given bucket and filepath, in JSONL format
    """
    # Initialize MinIO client
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    # Convert list of JSON objects to JSONL in memory
    jsonl_string = "\n".join(json.dumps(event) for event in events)
    jsonl_bytes = jsonl_string.encode("utf-8")
    jsonl_stream = io.BytesIO(jsonl_bytes)

    minio_client.put_object(
        bucket_name=bucket,
        object_name=filepath,
        data=jsonl_stream,
        length=len(jsonl_bytes),
        content_type="application/jsonl",
    )


def generate_page_load_events():
    """
    Generate a bunch of page-load events using Faker.
    """
    fake = Faker()
    names = [fake.name() for _ in range(20)]
    name_weights = [i for i in range(20)]
    pages = ["/home", "/about", "/contact", "/products", "/cart", "/checkout"]
    page_weights = [10, 2, 3, 2, 2, 1]
    browsers = ["Chrome", "Firefox", "Safari", "Edge"]
    browser_weights = [1, 3, 2, 3]

    events = []
    for i in range(1000):
        event = {
            "metadata": {
                "name": "page_load",
                "version": "v1",
                "timestamp": fake.date_time_between(
                    start_date="-7d", end_date="now"
                ).isoformat(),
            },
            "payload": {
                "page": random.choices(pages, weights=page_weights)[0],
                "user_name": random.choices(names, weights=name_weights)[0],
                "browser": random.choices(browsers, weights=browser_weights)[0],
            },
        }
        events.append(event)

    return events


def main():
    for i in range(10):
        id = uuid.uuid4().hex
        ts = datetime.datetime.now()
        events = generate_page_load_events()
        filepath = f"page_load/v1/{ts.year}/{ts.month}/{ts.day}/{id}.jsonl"
        push_events_to_minio(
            events=events,
            bucket="raw",
            filepath=filepath,
        )
        print(f"Pushed 1000 page_load events to: raw/{filepath}")


if __name__ == "__main__":
    main()

