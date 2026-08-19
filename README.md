# The Polite Scraper

A Python web scraping project created for the FlyRank AI Backend Development Internship.

## Target Classification

**Target:** Books to Scrape

**Purpose:** Books to Scrape is a practice sandbox created for learning and testing web scraping.

**Scope:** process the first 3 catalogue pages, which contain 60 books in total.

**Data collected:** Book title, product URL, price, availability, rating, description, source page and fetch time.

**Why this is appropriate:** The website is specifically provided as a sandbox for practising web scraping.

**robots.txt result:** No robots file found. The request returned 404 Not Found.

I will not reuse this code on another site without checking its rules and terms first.

## Technology

This project uses Python.

Libraries used:

- Requests
- Beautiful Soup
- Pydantic

## Setup

Clone the repository:

```bash
git clone https://github.com/Simply-Adam/Polite-Scraper
cd polite WebScraper
```
Create a virtual environment:
```bash
python -m venv venv
```
Activate it on Windows:
```bash
.\venv\Scripts\Activate.ps1
```
Install the dependencies:
```bash
pip install -r requirements.txt
```

Then run it:
```bash
python src/main.py
```

##Politeness Rules

The scraper follows several rules to reduce unnecessary traffic:

-Sends an identifying User-Agent.
-Uses a timeout for every request.
-Waits at least 500 ms between real requests.
-Checks HTTP status codes before parsing responses.
-Saves downloaded HTML to a local cache.
-Uses cached pages during later runs instead of requesting them again.
-Does not retry 403 or 404 responses.
-Retries a timeout or server error only once.


##Run Report

Example result from a completed run:

{
  "started_at": "2026-08-19T01:02:07Z",
  "duration_seconds": 2.27,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failed_urls": [
    {
      "url": "https://books.toscrape.com/catalogue/this-book-does-not-exist/index.html",
      "reason": "HTTP 404"
    }
  ]
}

##Limitation

The scraper depends on the current HTML structure of Books to Scrape. If the site's HTML or CSS classes change, some selectors may need to be updated.

##Ethics

When an official API exists, it should normally be used instead of scraping. A scraper should not bypass logins, paywalls, access restrictions or technical blocks, and should only collect the data needed for its purpose.