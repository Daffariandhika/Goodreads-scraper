#Goodreads-Scraper

A professional Python-based tool for efficiently scraping and analyzing book data from [Goodreads](https://www.goodreads.com). Designed for researchers, developers, and book enthusiasts who need structured and detailed book metadata in bulk.

---

## ✨ Overview

This project includes two main Python scripts that work together to collect and extract book information from Goodreads:

* **`url_scraper.py`** — Gathers book URLs based on a genre or search query.
* **`books_scraper.py`** — Scrapes detailed book data from the URLs collected.

Output is saved in both **JSON** and **CSV** formats for easy integration and analysis.

---

## 🌟 Features

### `url_scraper.py`

* Scrapes book URLs from a specific genre or search results page.
* Automatically handles pagination.
* Allows configuration for maximum number of URLs (`max_urls`).
* Saves extracted URLs into a Python file (`books_url.py`) for use in the next script.

### `books_scraper.py`

* Parses and extracts detailed book data from URLs.
* Includes retry logic for failed HTTP requests.
* Automatically rate-limits requests to avoid server blocks.
* Outputs structured data to `books.json` and `books.csv`.

---

## ⚙️ Prerequisites

Ensure you have **Python 3.10+** installed.
Install required packages:

```bash
pip install pandas requests beautifulsoup4
```

---

## 📄 Usage Guide

### 1. `url_scraper.py`

Collects Goodreads book URLs based on a search or genre page.

**Setup:**

* Modify the `genre_url` or `search_url` variable inside the script.
* Set `max_urls` to define how many book links to fetch.

**Run the script:**

```bash
python url_scraper.py
```

**Output:**

* Saves URLs to `books_url.py`

---

### 2. `books_scraper.py`

Scrapes detailed data from each book URL gathered earlier.

**Ensure:**

* `books_url.py` (output of the first script) is in the same directory.

**Run the script:**

```bash
python books_scraper.py
```

**Output:**

* `books.json` — Raw JSON format.
* `books.csv` — Tabular data for spreadsheets or databases.

---

## 🔧 Parameters & Configuration

### `url_scraper.py`

* `genre_url` or `search_url` — Goodreads URL to start scraping.
* `max_urls` — Maximum number of book URLs to collect.
* `delay` — Delay (in seconds) between requests.

### `books_scraper.py`

* Includes:

  * Rate limiting.
  * Automatic retries (up to 3 times per failed request).
  * Output file options (`books.json`, `books.csv`).

---

## 🔧 Tech Stack

<div align="left">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) ![Requests](https://img.shields.io/badge/Requests-005571?style=for-the-badge&logo=python&logoColor=white) ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4B0082?style=for-the-badge&logo=beautifulsoup&logoColor=white) ![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white) ![Logging](https://img.shields.io/badge/Logging-333333?style=for-the-badge&logo=python&logoColor=white) ![URLlib](https://img.shields.io/badge/urllib-007396?style=for-the-badge&logo=python&logoColor=white)

</div>

---

## ⚡ Troubleshooting

* **No URLs Found:**

  * Double-check the `search_url` or `genre_url` format.
  * Ensure the page has books listed and hasn’t changed its structure.

* **Script Fails to Scrape Data:**

  * Goodreads may be temporarily blocking requests. Try increasing delay.
  * Make sure `books_url.py` contains valid book URLs.

* **Empty Output Files:**

  * Check that URLs collected are reachable.
  * Review console output for errors or skipped entries.

---

## 🚀 Future Improvements

* Proxy support for large-scale scraping
* CLI support for dynamic URL input
* Integration with Goodreads APIs (if public access returns)

---

## 📚 License

This project is released under the MIT License.

---

Made with ❤️ for book lovers and data enthusiasts.
