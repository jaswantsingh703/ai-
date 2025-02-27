import requests
from bs4 import BeautifulSoup
from googlesearch import search
import logging

class WebBrowsing:
    def __init__(self):
        """
        Initialize the Web Browsing module for AI assistant.
        """
        self.session = requests.Session()

    def google_search(self, query, num_results=5):
        """
        Perform a Google search and return the top results.
        """
        try:
            results = [url for url in search(query, num=num_results, stop=num_results, pause=2)]
            return results
        except Exception as e:
            logging.error(f"Google search failed: {e}")
            return []

    def fetch_page_content(self, url):
        """
        Fetch and parse the content of a web page.
        """
        try:
            response = self.session.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                return soup.get_text()
            else:
                logging.error(f"Failed to fetch page content: {response.status_code}")
                return ""
        except Exception as e:
            logging.error(f"Error fetching page content: {e}")
            return ""

# Example Usage
if __name__ == "__main__":
    web_browser = WebBrowsing()
    query = "Latest AI trends 2025"
    search_results = web_browser.google_search(query)
    print("Top Search Results:", search_results)
    if search_results:
        content = web_browser.fetch_page_content(search_results[0])
        print("Extracted Page Content:", content[:500])
