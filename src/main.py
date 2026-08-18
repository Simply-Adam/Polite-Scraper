from pathlib import Path
import requests


PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_FILE = Path("cache/catalogue-page-1.html")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/Simply-Adam/Polite-Scraper)"
}

TIMEOUT = 10


def get_catalogue_page():

    #create cache folder if it doesn't exist
    CACHE_FILE.parent.mkdir(exist_ok=True)

    #use saved page if we already downloaded it
    if CACHE_FILE.exists():
        content = CACHE_FILE.read_bytes()

        print(f"CACHE HIT - {len(content)} bytes")

        return content

    print(f"FETCH - {PAGE_URL}")

    try:
        response = requests.get(
            PAGE_URL,
            headers=HEADERS,
            timeout=TIMEOUT
        )

    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return None

    #only accept successful responses
    if response.status_code != 200:
        print(f"Fetch failed with status {response.status_code}")
        return None

    content = response.content

    #save the HTML
    CACHE_FILE.write_bytes(content)

    print(f"FETCH complete - {len(content)} bytes")

    return content


def main():

    page = get_catalogue_page()

    if page is None:
        print("Could not load catalogue page.")
        return

    print("Catalogue page ready.")


if __name__ == "__main__":
    main()