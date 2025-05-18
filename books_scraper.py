import pandas as pd
import requests
import logging
import random
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from books_url import book_urls

# Constants
FALLBACK_IMAGE = "https://via.placeholder.com/150?text=No+Image+Available"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}
RETRY_COUNT = 3
RATE_LIMIT_DELAY = (1, 3)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def is_valid_url(url):
    """
    Validate a URL.
    Args:
        url (str): URL string to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])


def fetch_url_with_retries(url, retries=RETRY_COUNT):
    """
    Fetch a URL with retries in case of failure.
    Args:
        url (str): URL to fetch.
        retries (int): Number of retry attempts.
    Returns:
        Response: Response object if successful, None otherwise.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response
            logging.warning(f"Attempt {attempt + 1} failed with status code {response.status_code}.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(2)  # Wait before retrying
    logging.error(f"Failed to fetch URL after {retries} attempts: {url}")
    return None


def scrape_goodreads_book(book_url):
    """
    Scrape details of a book from Goodreads.
    Args:
        book_url (str): URL of the Goodreads book page.
    Returns:
        dict: Scraped book data or None if scraping fails.
    """
    response = fetch_url_with_retries(book_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        book_title = soup.find("h1", {"data-testid": "bookTitle"}).get_text(strip=True) or "N/A"
        author_name = soup.find("a", {"class": "ContributorLink"}).get_text(strip=True) or "N/A"
        image_tag = soup.find("img", {"class": "ResponsiveImage"})
        image_url = image_tag["src"] if image_tag else FALLBACK_IMAGE
        description_div = soup.find("div", {"data-testid": "description"})
        description = (
            description_div.get_text(strip=True).split('.')[0] + '.'
            if description_div and '.' in description_div.get_text(strip=True) else "No description available."
        )
        genres_section = soup.find("div", {"data-testid": "genresList"})
        genres = [
            genre.get_text(strip=True)
            for genre in genres_section.select("a.Button--tag.Button--medium span.Button__labelItem")
        ][:2] if genres_section else ["General"]
        price = random.randint(10, 200) * 1000
        likes = random.randint(1, 100)
        stock = random.randint(1, 10)
        rating_tag = soup.find("div", {"class": "RatingStatistics__rating"})
        average_rating = float(rating_tag.get_text(strip=True)) if rating_tag else 0.0

        book_data = {
            "title": book_title,
            "authorName": author_name,
            "imageURL": image_url,
            "description": description,
            "category": genres,
            "price": price,
            "likes": likes,
            "stock": stock,
            "averageRating": average_rating,
        }

        logging.info(f"Scraped data for book: {book_title}")
        return book_data
    except Exception as error:
        logging.error(f"Error occurred while parsing {book_url}: {error}")
        return None


def scrape_multiple_books(book_urls):
    """
    Scrape book details from multiple Goodreads URLs.
    Args:
        book_urls (list): List of Goodreads book URLs.
    Returns:
        list: List of book data dictionaries.
    """
    books_data = []
    for url in book_urls:
        if not is_valid_url(url):
            logging.warning(f"Invalid URL skipped: {url}")
            continue
        book_data = scrape_goodreads_book(url)
        if book_data:
            books_data.append(book_data)
        time.sleep(random.uniform(*RATE_LIMIT_DELAY))  # Rate-limiting to avoid bans
    return remove_duplicates(books_data)


def remove_duplicates(data):
    """
    Remove duplicate books by title.
    Args:
        data (list): List of book dictionaries.
    Returns:
        list: List of unique book dictionaries.
    """
    seen = set()
    unique_books = []
    for book in data:
        if book["title"] not in seen:
            seen.add(book["title"])
            unique_books.append(book)
    return unique_books


def save_data(data, file_format="json", filename="books_data"):
    """
    Save book data to a file in JSON or CSV format.
    Args:
        data (list): List of book data dictionaries.
        file_format (str): File format ('json' or 'csv').
        filename (str): Output file name.
    """
    if file_format == "json":
        save_data_to_json(data, f"{filename}.json")
    elif file_format == "csv":
        save_data_to_csv(data, f"{filename}.csv")
    else:
        logging.warning(f"Unsupported file format: {file_format}")


def save_data_to_json(data, filename):
    """
    Save data to a JSON file.
    Args:
        data (list): List of book data dictionaries.
        filename (str): JSON file name.
    """
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
    """
    Save data to a CSV file.
    Args:
        data (list): List of book data dictionaries.
        filename (str): CSV file name.
    """
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
    """
    Main script execution:
    - Fetch book URLs from the `goodreads_books_urls.py` file.
    - Scrape data for each book.
    - Save the scraped data in both JSON and CSV formats.
    """
    scraped_books = scrape_multiple_books(book_urls)
    save_data(scraped_books, file_format="json", filename="books")
    save_data(scraped_books, file_format="csv", filename="books")
    logging.info("Scraping and saving completed.")
