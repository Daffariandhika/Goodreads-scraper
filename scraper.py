"""
scraper.py

This script scrapes detailed book information from Goodreads book pages given a list of URLs.
It handles HTTP request retries, respects rate limits by random delays between requests,
extracts various book metadata, and saves the aggregated data in JSON and CSV formats.

Main Features:
    - Validates URLs before scraping.
    - Robust retry mechanism for HTTP requests.
    - Extracts book title, author, description, ISBN, publication date, page count, categories, average rating, total ratings, total reviews, price (simulated), stock (simulated), likes (simulated), and image URL.
    - Parses and normalizes publication dates into YYYY-MM-DD format.
    - Handles missing or malformed data gracefully with fallbacks.
    - Removes duplicate books by title before saving.
    - Saves aggregated book data to JSON and CSV files, appending to existing data if files exist.
    - Configurable rate limiting to avoid overloading Goodreads servers.
    - Logs progress, warnings, and errors.

Usage:
    Run from the command line:
        python scraper.py

Example JSON Output:
    [
        {
            "title": "Fight Club",
            "authorName": "Chuck Palahniuk",
            "description": "Chuck Palahniuk showed himself to be his generation",
            "isbn": "9780393355949",
            "publication": "1996-08-17",
            "pages": 224,
            "category": [
                "Fiction",
                "Classics",
                "Thriller",
                "Contemporary",
                "Novels",
                "Mystery",
                "Literature"
            ],
            "likes": 69,
            "averageRating": 4.18,
            "totalRating": 625058,
            "totalReview": 25009,
            "price": 57000,
            "stock": 7,
            "imageURL": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1558216416i/36236124.jpg"
        },
        ...
    ]

Best Practices:
    - Avoid too aggressive scraping to prevent IP blocking.
    - Use realistic delays and limit the number of requests per session.

Author:
    Riandhika (2025)
    License: MIT
"""

import pandas as pd
import requests
import logging
import random
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dateutil import parser
import re
from list import book_urls

FALLBACK_IMAGE = "https://img.freepik.com/premium-photo/crisp-white-watercolor-paper-texture-background_707519-26089.jpg?semt=ais_hybrid&w=740"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}
RETRY_COUNT = 3
RATE_LIMIT_DELAY = (1, 3)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def fetch_url_with_retries(url, retries=RETRY_COUNT):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response
            logging.warning(f"Attempt {attempt + 1} failed with status code {response.status_code}.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(2)
    logging.error(f"Failed to fetch URL after {retries} attempts: {url}")
    return None

def extract_isbn(soup, html_text):
    isbn_divs = soup.find_all('div', class_='TruncatedContent__text TruncatedContent__text--small', attrs={'data-testid': 'contentContainer'})
    for div in isbn_divs:
        text = div.get_text(strip=True)
        if text and text[:3].isdigit() and len(text.split()[0]) >= 10:
            return text.split()[0]
    match = re.search(r'\b97[89][\d]{10}\b', html_text)
    return match.group(0) if match else "N/A"

def extract_int_from_text(text):
    return int(re.sub(r"[^\d]", "", text)) if text else 0

def extract_publication_date(soup):
    pub_tag = soup.find("p", {"data-testid": "publicationInfo"})
    if not pub_tag:
        return "N/A"

    text = pub_tag.get_text(strip=True)

    match = re.search(r'(?:First published|Published)\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})', text)
    if match:
        date_str = match.group(1)
    else:
        match = re.search(r'(?:First published|Published)\s+([A-Za-z]+\s+\d{4})', text)
        if match:
            date_str = match.group(1)
        else:
            match = re.search(r'(?:First published|Published)\s+(\d{4})', text)
            if match:
                date_str = match.group(1)
            else:
                return "N/A"
    try:
        dt = parser.parse(date_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return "N/A"

def scrape_goodreads_book(book_url):
    response = fetch_url_with_retries(book_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        book_title = soup.find("h1", {"data-testid": "bookTitle"}).get_text(strip=True) or "N/A"
        author_name = soup.find("a", {"class": "ContributorLink"}).get_text(strip=True) or "N/A"
        pages_tag = soup.find("p", {"data-testid": "pagesFormat"})
        if pages_tag:
            pages_text = pages_tag.get_text(strip=True)
            match = re.search(r'(\d+)\s+pages', pages_text, re.IGNORECASE)
            pages = int(match.group(1)) if match else "N/A"
        else:
            pages = "N/A"
        publication = extract_publication_date(soup)
        image_tag = soup.find("img", {"class": "ResponsiveImage"})
        image_url = image_tag["src"] if image_tag else FALLBACK_IMAGE
        description_div = soup.find('div', {'data-testid': 'contentContainer'}).get_text(strip=True) or "N/A"
        genres_section = soup.find("div", {"data-testid": "genresList"})
        genres = [
            genre.get_text(strip=True)
            for genre in genres_section.select("a.Button--tag.Button--medium span.Button__labelItem")
        ] if genres_section else ["General"]
        isbn = extract_isbn(soup, response.text)
        price = random.randint(10, 200) * 1000
        likes = random.randint(1, 100)
        stock = random.randint(1, 10)
        rating_tag = soup.find("div", {"class": "RatingStatistics__rating"})
        average_rating = float(rating_tag.get_text(strip=True)) if rating_tag else 0.0
        ratings_tag = soup.find("span", {"data-testid": "ratingsCount"})
        reviews_tag = soup.find("span", {"data-testid": "reviewsCount"})
        ratings_count = extract_int_from_text(ratings_tag.get_text()) if ratings_tag else 0
        reviews_count = extract_int_from_text(reviews_tag.get_text()) if reviews_tag else 0

        book_data = {
            "title": book_title,
            "authorName": author_name,
            "description": description_div,
            "isbn": isbn,
            "publication": publication,
            "pages": pages,
            "category": genres,
            "likes": likes,
            "averageRating": average_rating,
            "totalRating": ratings_count,
            "totalReview": reviews_count,
            "price": price,
            "stock": stock,
            "imageURL": image_url,
        }
        logging.info(f"Scraped data for book: {book_title}")
        return book_data
    except Exception as error:
        logging.error(f"Error occurred while parsing {book_url}: {error}")
        return None

def scrape_multiple_books(book_urls):
    books_data = []
    for url in book_urls:
        if not is_valid_url(url):
            logging.warning(f"Invalid URL skipped: {url}")
            continue
        book_data = scrape_goodreads_book(url)
        if book_data:
            books_data.append(book_data)
        time.sleep(random.uniform(*RATE_LIMIT_DELAY))
    return remove_duplicates(books_data)

def remove_duplicates(data):
    seen = set()
    unique_books = []
    for book in data:
        if book["title"] not in seen:
            seen.add(book["title"])
            unique_books.append(book)
    return unique_books

def save_data(data, file_format="json", filename="data"):
    if file_format == "json":
        save_data_to_json(data, f"{filename}.json")
    elif file_format == "csv":
        save_data_to_csv(data, f"{filename}.csv")
    else:
        logging.warning(f"Unsupported file format: {file_format}")

def save_data_to_json(data, filename):
    try:
        try:
            with open(filename, "r") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        updated_data = existing_data + data
        with open(filename, "w") as file:
            json.dump(updated_data, file, indent=4)
        logging.info(f"Data successfully saved to {filename}")
    except Exception as error:
        logging.error(f"Error saving data to JSON: {error}")

def save_data_to_csv(data, filename):
    try:
        try:
            existing_data = pd.read_csv(filename)
            new_data = pd.DataFrame(data)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except FileNotFoundError:
            updated_data = pd.DataFrame(data)

        updated_data.to_csv(filename, index=False)
        logging.info(f"Data successfully saved to {filename}")
    except Exception as error:
        logging.error(f"Error saving data to CSV: {error}")

if __name__ == "__main__":
    scraped_books = scrape_multiple_books(book_urls)
    save_data(scraped_books, file_format="json", filename="data")
    save_data(scraped_books, file_format="csv", filename="data")
    logging.info("Scraping and saving completed.")
