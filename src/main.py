from pathlib import Path
from urllib.parse import urljoin
import time

import requests
from bs4 import BeautifulSoup


START_URL = "https://books.toscrape.com/catalogue/page-1.html"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/Simply-Adam/Polite-Scraper)"
}

TIMEOUT = 10
REQUEST_DELAY = 0.5


def fetch_page(url, cache_file):

    cache_file = Path(cache_file)

    #make sure the cache folder exists
    cache_file.parent.mkdir(exist_ok=True)

    #use cached HTML if we already have it
    if cache_file.exists():
        content = cache_file.read_bytes()

        print(f"CACHE HIT - {url} - {len(content)} bytes")

        return content

    #wait before making a real request
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

    if response.status_code != 200:
        print(f"Fetch failed with status {response.status_code}")
        return None

    content = response.content

    cache_file.write_bytes(content)

    print(f"FETCH complete - {len(content)} bytes")

    return content


def discover_books():

    current_url = START_URL
    page_number = 1

    book_urls = []

    while page_number <= 3:

        cache_file = f"cache/catalogue-page-{page_number}.html"

        html = fetch_page(current_url, cache_file)

        if html is None:
            print("Could not load catalogue page.")
            break

        # parse the HTML
        soup = BeautifulSoup(html, "html.parser")

        # find all book links
        book_links = soup.select("article.product_pod h3 a")

        for link in book_links:

            href = link.get("href")

            if href:
                full_url = urljoin(current_url, href)
                book_urls.append(full_url)

        # find the next page link
        next_link = soup.select_one("li.next a")

        if next_link is None:
            break

        next_href = next_link.get("href")

        if not next_href:
            break

        current_url = urljoin(current_url, next_href)

        page_number += 1

    unique_urls = list(dict.fromkeys(book_urls))

    print()
    print(f"catalogue_pages={page_number}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls


def main():

    books = discover_books()

    print()
    print("First 5 book URLs:")

    for url in books[:5]:
        print(url)


if __name__ == "__main__":
    main()