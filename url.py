"""
url.py

This script extracts unique Goodreads book URLs from shelf, search, or list pages. It automates pagination,
avoids duplicates, and respects rate limits by optionally delaying requests between pages.

Main Features:
    Supports Goodreads shelf/search/list URLs.
    Automatically follows pagination.
    Extracts up to a user-defined number of unique book URLs.
    Skips duplicate links.
    Delays requests to reduce load on Goodreads.
    Saves results to a Python `.py` file as a list named `book_urls`.

Usage:
    Run from the command line:
        python url.py --url https://www.goodreads.com/shelf/show/fantasy --max 50 --delay 1 --output books.py

Arguments:
    --url     (str) : Required. Goodreads shelf/search/list page URL to begin scraping.
    --max     (int) : Optional. Max number of book URLs to extract. Default: 20.
    --delay   (int) : Optional. Delay in seconds between page requests. Default: 2.
    --output  (str) : Optional. Output filename where the list will be saved. Default: "list.py".

Example Output:
    book_urls = [
        "https://www.goodreads.com/book/show/12345.Book_Title",
        "https://www.goodreads.com/book/show/67890.Another_Book_Title",
        ...
    ]

Best Practices:
    Do not scrape too aggressively; Goodreads may throttle or block requests.

Author:
    Riandhika (2025)
    License: MIT

"""

import argparse
import requests
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import sys
import os

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Scrape unique book URLs from Goodreads shelf/search/list pages.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--url", type=str, required=True, help="Goodreads shelf/search/list URL to scrape")
    parser.add_argument("--max", type=int, default=20, help="Max number of book URLs to scrape")
    parser.add_argument("--delay", type=int, default=2, help="Delay between page requests (in seconds)")
    parser.add_argument("--output", type=str, default="list.py", help="Output filename (e.g. books.py)")
    return parser.parse_args()

def update_pagination_url(base_url, page_number):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query)
    params['page'] = [str(page_number)]
    updated_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=updated_query))

def fetch_goodreads_urls(base_url, max_urls=20, delay=2):
    print("[INFO] Starting Goodreads scraping session...")
    page = 1
    seen_urls = set()
    book_urls = []

    while len(book_urls) < max_urls:
        paginated_url = update_pagination_url(base_url, page)
        print(f"[INFO] Fetching page {page}: {paginated_url}")

        try:
            response = requests.get(paginated_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Request failed on page {page}: {e}")
            print("[INFO] Stopping due to network error.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        book_links = soup.find_all("a", class_="bookTitle", href=True)

        if not book_links:
            print("[INFO] No book links found on this page. Possibly last page.")
            break

        new_links = 0
        for tag in book_links:
            full_url = "https://www.goodreads.com" + tag['href']
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                book_urls.append(full_url)
                new_links += 1
                if len(book_urls) >= max_urls:
                    break

        print(f"[INFO] Found {new_links} new URLs on page {page}. Total: {len(book_urls)}/{max_urls}")
        page += 1
        time.sleep(delay)

    print(f"[DONE] Scraped {len(book_urls)} unique book URLs.")
    return book_urls

def save_urls_to_file(urls, filename):
    if not filename.endswith(".py"):
        filename += ".py"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("book_urls = [\n")
            for url in urls:
                f.write(f'    "{url}",\n')
            f.write("]\n")
        print(f"[SUCCESS] Book URLs saved to: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"[ERROR] Failed to write output to {filename}: {e}")
        sys.exit(1)

def main():
    args = parse_args()

    print(f"\n[CONFIG] Target URL:   {args.url}")
    print(f"[CONFIG] Max URLs:     {args.max}")
    print(f"[CONFIG] Delay:        {args.delay} second(s)")
    print(f"[CONFIG] Output file:  {args.output}\n")

    urls = fetch_goodreads_urls(args.url, args.max, args.delay)

    if urls:
        save_urls_to_file(urls, args.output)
    else:
        print("[WARNING] No URLs collected. Output file was not created.")

if __name__ == "__main__":
    main()