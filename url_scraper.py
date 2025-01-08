import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Define user-agent to mimic a real browser. This helps avoid blocks or detection as a bot.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}

def update_pagination_url(base_url, page):
    """
    Updates the URL for the desired page in Goodreads search or genre results.

    Args:
        base_url (str): The initial URL for the first page of the results.
        page (int): The page number to navigate to.

    Returns:
        str: A properly formatted URL with the updated page number.

    Workflow:
        - Parse the URL into components.
        - Modify the 'page' query parameter in the URL.
        - Reconstruct the URL with the updated query string.
    """
    parsed_url = urlparse(base_url)
    query_params = parse_qs(parsed_url.query)
    query_params['page'] = [page]  # Set the 'page' parameter to the desired value
    new_query = urlencode(query_params, doseq=True)
    updated_url = urlunparse(parsed_url._replace(query=new_query))
    return updated_url

def fetch_goodreads_urls(genre_url, max_urls=20, delay=2):
    """
    Scrapes Goodreads for book URLs from a specific genre or search results.

    Args:
        genre_url (str): The starting URL for the Goodreads genre or search results.
        max_urls (int): Maximum number of book URLs to fetch (default: 50).
        delay (int): Delay between requests (default: 2 seconds).

    Returns:
        list: A list containing unique book URLs scraped from the site.

    Workflow:
        - Start at page 1 of the genre or search results.
        - Fetch the page using `requests`.
        - Parse the page with `BeautifulSoup` to extract book links.
        - Continue to subsequent pages until the maximum URLs are collected or no more pages are available.
        - Introduce a delay between page requests to avoid overloading the server.
    """
    book_urls = []  # List to store unique book URLs
    page = 1  # Initial page number

    while len(book_urls) < max_urls:
        print(f"Scraping page {page}... (Collected {len(book_urls)} of {max_urls} URLs)")
        paginated_url = update_pagination_url(genre_url, page)  # Generate URL for the current page

        try:
            # Fetch the page content
            response = requests.get(paginated_url, headers=HEADERS)
            if response.status_code != 200:  # Handle HTTP errors
                print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
                break

            # Parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract book links using their HTML class
            book_links = soup.find_all("a", {"class": "bookTitle"}, href=True)
            if not book_links:  # Stop if no links are found (end of results)
                print("No more book links found. Reached the end of the section.")
                break

            # Add the links to the list, avoiding duplicates
            for link in book_links:
                full_url = "https://www.goodreads.com" + link["href"]
                if full_url not in book_urls:
                    book_urls.append(full_url)
                    if len(book_urls) >= max_urls:  # Stop if the limit is reached
                        break

            # Move to the next page and pause to respect server limits
            page += 1
            time.sleep(delay)

        except Exception as error:
            print(f"An error occurred while scraping page {page}: {error}")
            break

    print(f"Scraped {len(book_urls)} book URLs from the section.")
    return book_urls

def save_urls_as_array(urls, filename="book_urls.py"):
    """
    Saves the scraped book URLs into a Python file as a list.

    Args:
        urls (list): The list of book URLs to save.
        filename (str): The name of the file to save the URLs (default: 'book_urls.py').

    Workflow:
        - Open the file in write mode.
        - Write the URLs into the file in a Python list format.
        - Handle any file I/O exceptions gracefully.
    """
    try:
        with open(filename, "w") as file:
            file.write("book_urls = [\n")  # Start the list
            for url in urls:
                file.write(f'    "{url}",\n')  # Write each URL as a string
            file.write("]\n")  # End the list
        print(f"URLs saved as an array in {filename}")
    except Exception as error:
        print(f"Error saving URLs to file: {error}")

if __name__ == "__main__":
    """
    Main execution block.
    
    - Defines the initial Goodreads URL to scrape.
    - Specifies the maximum number of URLs to fetch and delay between requests.
    - Calls the scraping function to fetch book URLs.
    - Saves the scraped URLs into a Python file for later use.
    """
    # Example Goodreads genre URL (change as needed)
    goodreads_search_url = "https://www.goodreads.com/shelf/show/historical"

    # Define the scraping parameters
    max_urls_to_fetch = 20  # Number of book URLs to collect
    delay_between_requests = 2  # Delay in seconds between each request

    # Fetch book URLs and save them
    all_book_urls = fetch_goodreads_urls(
        genre_url=goodreads_search_url,
        max_urls=max_urls_to_fetch,
        delay=delay_between_requests
    )

    # Save the collected URLs to a Python file
    save_urls_as_array(all_book_urls, "books_url.py")