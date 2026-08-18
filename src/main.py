from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone
import json
import time

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError


START_URL = "https://books.toscrape.com/catalogue/page-1.html"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/Simply-Adam/Polite-Scraper)"
}

TIMEOUT = 10
REQUEST_DELAY = 0.5

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None = None
    source_page: str
    fetched_at: str


def fetch_page(url, cache_file):

    cache_file = Path(cache_file)

    #create cache folders if needed
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    #read from cache if page already exists
    if cache_file.exists():
        content = cache_file.read_bytes()

        print(f"CACHE HIT - {url}")

        return content

    #wait before a real request
    time.sleep(REQUEST_DELAY)

    print(f"FETCH - {url}")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return None

    # only accept successful responses
    if response.status_code != 200:
        print(f"Fetch failed with status {response.status_code}")
        return None

    content = response.content

    # save HTML to cache
    cache_file.write_bytes(content)

    print(f"FETCH complete - {len(content)} bytes")

    return content


def get_fetched_at(cache_file):

    cache_file = Path(cache_file)

    timestamp = cache_file.stat().st_mtime

    fetched_time = datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc
    )

    return fetched_time.isoformat(timespec="seconds").replace("+00:00", "Z")


def discover_books():

    current_url = START_URL

    catalogue_pages = 0
    discovered = 0

    books = []
    seen_urls = set()

    while catalogue_pages < 3:

        page_number = catalogue_pages + 1

        cache_file = f"cache/catalogue-page-{page_number}.html"

        html = fetch_page(current_url, cache_file)

        if html is None:
            print("Could not load catalogue page.")
            break

        soup = BeautifulSoup(html, "html.parser")

        book_links = soup.select("article.product_pod h3 a")

        for link in book_links:
            
            href = link.get("href")

            if not href:
                continue

            discovered += 1

            full_url = urljoin(current_url, href)

            # only keep each book once
            if full_url not in seen_urls:

                seen_urls.add(full_url)

                books.append({
                    "product_url": full_url,
                    "source_page": current_url
                })

        catalogue_pages += 1

        #stop after page 3
        if catalogue_pages == 3:
            break

        #find next catalogue page
        next_link = soup.select_one("li.next a")

        if next_link is None:
            break

        next_href = next_link.get("href")

        if not next_href:
            break

        current_url = urljoin(current_url, next_href)

    print()
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={discovered}")
    print(f"unique_urls={len(books)}")

    return books


def get_book_cache_file(product_url):

    parsed_url = urlparse(product_url)

    book_name = Path(parsed_url.path).parent.name

    return Path("cache/books") / f"{book_name}.html"


def extract_book(book):
    product_url = book["product_url"]
    source_page = book["source_page"]

    cache_file = get_book_cache_file(product_url)

    html = fetch_page(product_url,cache_file)

    if html is None:
        return None

    soup = BeautifulSoup(html,"html.parser")

    #main product area
    product_main = soup.select_one("div.product_main")

    if product_main is None:
        print(f"Product area not found: {product_url}")
        return None

    #title
    title_element = product_main.select_one("h1")

    title = (
        title_element.get_text(strip=True)
        if title_element
        else None
    )

    #price
    price_element = product_main.select_one("p.price_color")

    price_text = (
        price_element.get_text(strip=True)
        if price_element
        else None
    )

    #availability
    availability_element = product_main.select_one("p.availability")

    availability_text = (
        availability_element.get_text(" ",strip=True)
        if availability_element
        else None
    )

    #rating
    rating_element = product_main.select_one("p.star-rating")

    rating_text = None

    if rating_element:
        classes = rating_element.get("class",[])

        for class_name in classes:
            if class_name != "star-rating":
                rating_text = class_name
                break

    #description
    description = None
    description_heading = soup.select_one("#product_description")

    if description_heading:
        description_element = (description_heading.find_next_sibling("p"))

        if description_element:
            description = description_element.get_text(" ", strip=True)

    #create raw record
    record = {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": get_fetched_at(cache_file)
    }

    return record


def extract_all_books(books):

    records = []

    for number, book in enumerate(
        books,
        start=1
    ):

        print()
        print(f"DETAIL {number}/{len(books)}")

        record = extract_book(book)

        if record is not None:
            records.append(record)

    return records


def validate_records(raw_records):

    valid_records = []
    errors = []

    for record in raw_records:

        try:
            finished_record = {
                **record,
                "price_gbp": normalize_price(record.get("price_text"))
            }

            validated_book = BookRecord(**finished_record)

            valid_records.append(validated_book.model_dump())

        except (ValidationError, ValueError) as error:

            errors.append({
                "product_url": record.get(
                    "product_url"
                ),
                "error": str(error)
            })

    return valid_records, errors


def normalize_price(price_text):

    if not price_text:
        raise ValueError("Price is missing")

    cleaned_price = price_text.replace("£", "").strip()

    return float(cleaned_price)


def save_output(valid_records, errors):

    output_folder = Path("output")

    output_folder.mkdir(
        exist_ok=True
    )

    books_file = output_folder / "books.json"
    errors_file = output_folder / "errors.json"

    books_file.write_text(
        json.dumps(
            valid_records,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    errors_file.write_text(
        json.dumps(
            errors,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

def main():

    books = discover_books()

    raw_records = extract_all_books(books)

    valid_records, errors = validate_records(
        raw_records
    )

    save_output(
        valid_records,
        errors
    )

    print()
    print("Validation complete")
    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")

    if valid_records:

        print()
        print("Sample validated record:")

        print(
            json.dumps(
                valid_records[0],
                indent=2,
                ensure_ascii=False
            )
        )


if __name__ == "__main__":
    main()