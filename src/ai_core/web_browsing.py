import requests
import logging
from bs4 import BeautifulSoup
from src.utils.config import Config

# Check if googlesearch is available
try:
    from googlesearch import search
    GOOGLESEARCH_AVAILABLE = True
except ImportError:
    GOOGLESEARCH_AVAILABLE = False
    logging.warning("googlesearch-python module not available.")

class WebBrowsing:
    """
    Web browsing module for searching and fetching web content.
    """
    
    def __init__(self, api_key=None, search_engine_id=None):
        """
        Initialize the Web Browsing module with API keys from config.
        """
        self.session = requests.Session()
        
        # Set default headers to avoid blocks
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        })
        
        # Get API keys from config or parameters
        self.google_api_key = api_key or Config.get("google_search_api_key", "")
        self.search_engine_id = search_engine_id or Config.get("google_search_engine_id", "")
        
        logging.info("Web Browsing module initialized")

    def google_search(self, query, num_results=5):
        """
        Perform a Google search and return the top results.
        """
        if not query:
            return []
            
        try:
            if GOOGLESEARCH_AVAILABLE:
                results = [url for url in search(query, num=num_results, stop=num_results, pause=2)]
                return results
            else:
                logging.warning("Google search unavailable: googlesearch-python module not installed")
                return self._fallback_search(query)
        except Exception as e:
            logging.error(f"Google search failed: {e}")
            return self._fallback_search(query)

    def _fallback_search(self, query):
        """
        Provide a fallback when search functionality is unavailable.
        """
        logging.info("Using fallback search")
        return ["Search functionality unavailable. Please install googlesearch-python."]

    def fetch_page_content(self, url):
        """
        Fetch and parse the content of a web page.
        """
        if not url or not url.startswith(("http://", "https://")):
            return "Invalid URL provided."
            
        try:
            response = self.session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                # Get text
                text = soup.get_text(separator='\n')
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return text
            else:
                logging.error(f"Failed to fetch page content: {response.status_code}")
                return f"Failed to fetch content. Status code: {response.status_code}"
        except Exception as e:
            logging.error(f"Error fetching page content: {e}")
            return f"Error fetching content: {str(e)}"