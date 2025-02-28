import logging
import re
import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urlparse, urljoin
from src.utils.config import Config
from src.security.ai_security import AISecurity

class WebScraping:
    """
    Web scraping module for retrieving and processing web content.
    Provides safe tools for collecting information from the internet.
    """
    
    def __init__(self):
        """Initialize the web scraping module with safety measures."""
        # Load throttling settings from config
        self.request_delay = Config.get("web_request_delay", 1.0)  # seconds between requests
        self.max_pages_per_domain = Config.get("max_pages_per_domain", 5)
        self.max_content_length = Config.get("max_content_length", 500000)  # ~500KB
        self.timeout = Config.get("web_request_timeout", 10)
        
        # Initialize security
        self.security = AISecurity()
        
        # Tracking for rate limiting
        self.last_request_time = {}  # domain -> timestamp
        self.domain_request_count = {}  # domain -> count
        
        # Create session with reasonable headers
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; JarvisAssistant/1.0; +https://www.example.com/bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        })
        
        logging.info("Web Scraping module initialized")
    
    def fetch_url(self, url):
        """
        Safely fetch content from a URL with rate limiting and size restrictions.
        
        Args:
            url (str): URL to fetch
            
        Returns:
            tuple: (success, content or error message)
        """
        # Validate URL
        if not self._is_url_safe(url):
            logging.warning(f"Unsafe URL rejected: {url}")
            return False, "URL appears to be unsafe or malformed"
        
        # Extract domain for rate limiting
        domain = urlparse(url).netloc
        
        # Check domain request count
        if domain in self.domain_request_count and self.domain_request_count[domain] >= self.max_pages_per_domain:
            logging.warning(f"Rate limit exceeded for domain: {domain}")
            return False, f"Rate limit exceeded for {domain}. Maximum {self.max_pages_per_domain} requests allowed."
        
        # Apply rate limiting
        current_time = time.time()
        if domain in self.last_request_time:
            elapsed = current_time - self.last_request_time[domain]
            if elapsed < self.request_delay:
                time.sleep(self.request_delay - elapsed)
        
        # Update tracking
        self.last_request_time[domain] = time.time()
        self.domain_request_count[domain] = self.domain_request_count.get(domain, 0) + 1
        
        # Make the request
        try:
            logging.info(f"Fetching URL: {url}")
            response = self.session.get(
                url,
                timeout=self.timeout,
                stream=True  # Enable streaming for size checks
            )
            
            # Check status code
            if response.status_code != 200:
                logging.warning(f"Failed to fetch URL {url}: Status code {response.status_code}")
                return False, f"Failed to retrieve content: Status code {response.status_code}"
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if not ('text/html' in content_type or 'application/json' in content_type or 'text/plain' in content_type):
                logging.warning(f"Unsupported content type for {url}: {content_type}")
                return False, f"Unsupported content type: {content_type}"
            
            # Check content length
            content_length = int(response.headers.get('Content-Length', 0))
            if content_length > self.max_content_length:
                logging.warning(f"Content too large for {url}: {content_length} bytes")
                return False, f"Content too large: {content_length} bytes (max {self.max_content_length})"
            
            # Get content (with size check)
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.max_content_length:
                    logging.warning(f"Content exceeded max size during streaming for {url}")
                    return False, f"Content exceeded maximum size of {self.max_content_length} bytes"
            
            return True, content.decode('utf-8', errors='replace')
            
        except requests.exceptions.Timeout:
            logging.warning(f"Request timeout for URL: {url}")
            return False, "Request timed out"
            
        except requests.exceptions.TooManyRedirects:
            logging.warning(f"Too many redirects for URL: {url}")
            return False, "Too many redirects"
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return False, f"Error retrieving content: {str(e)}"
    
    def extract_text(self, html_content):
        """
        Extract readable text content from HTML.
        
        Args:
            html_content (str): HTML content
            
        Returns:
            str: Extracted text
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logging.error(f"Error extracting text from HTML: {e}")
            return ""
    
    def parse_article(self, html_content, url=""):
        """
        Parse an article from HTML content.
        
        Args:
            html_content (str): HTML content
            url (str): Original URL for reference
            
        Returns:
            dict: Parsed article data
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            article = {
                "url": url,
                "title": "",
                "author": "",
                "date": "",
                "content": "",
                "summary": ""
            }
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                article["title"] = title_tag.text.strip()
            else:
                # Try to find heading tags
                for heading in ['h1', 'h2']:
                    heading_tag = soup.find(heading)
                    if heading_tag:
                        article["title"] = heading_tag.text.strip()
                        break
            
            # Extract author
            author_candidates = [
                soup.find('meta', {'name': 'author'}),
                soup.find('meta', {'property': 'article:author'}),
                soup.find(class_=['author', 'byline'])
            ]
            for candidate in author_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        article["author"] = candidate.get('content', '')
                    else:
                        article["author"] = candidate.text.strip()
                    if article["author"]:
                        break
            
            # Extract date
            date_candidates = [
                soup.find('meta', {'name': 'date'}),
                soup.find('meta', {'property': 'article:published_time'}),
                soup.find(class_=['date', 'published', 'time', 'timestamp'])
            ]
            for candidate in date_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        article["date"] = candidate.get('content', '')
                    else:
                        article["date"] = candidate.text.strip()
                    if article["date"]:
                        break
            
            # Extract main content
            content_candidates = [
                soup.find('article'),
                soup.find(class_=['content', 'entry-content', 'post-content', 'article-content']),
                soup.find('main')
            ]
            
            for candidate in content_candidates:
                if candidate:
                    # Remove non-content elements from the candidate
                    for element in candidate(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
                        element.decompose()
                    
                    article["content"] = candidate.get_text(separator='\n').strip()
                    if article["content"]:
                        break
            
            # If no content found, use the full body text
            if not article["content"]:
                body = soup.find('body')
                if body:
                    # Remove non-content elements
                    for element in body(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
                        element.decompose()
                    
                    article["content"] = body.get_text(separator='\n').strip()
            
            # Create a summary (first few sentences)
            if article["content"]:
                sentences = re.split(r'(?<=[.!?])\s+', article["content"])
                article["summary"] = ' '.join(sentences[:3])
            
            return article
            
        except Exception as e:
            logging.error(f"Error parsing article: {e}")
            return {
                "url": url,
                "title": "Error parsing article",
                "content": "",
                "error": str(e)
            }
    
    def search_for_information(self, query, max_results=3):
        """
        Search for information using a search engine or directly hitting URLs.
        This method requires an external search API (like Google Custom Search API).
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: Search results
        """
        # Get search API keys from config
        api_key = Config.get("google_search_api_key", "")
        search_engine_id = Config.get("google_search_engine_id", "")
        
        if not api_key or not search_engine_id:
            logging.warning("Google Search API key or engine ID not configured")
            return [{"error": "Search functionality not available. Configure API keys in settings."}]
        
        try:
            # Use Google Custom Search API
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "num": max_results
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code != 200:
                logging.error(f"Search API error: {response.status_code}")
                return [{"error": f"Search API error: {response.status_code}"}]
            
            data = response.json()
            results = []
            
            # Extract search results
            if "items" in data:
                for item in data["items"]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
            
            return results
            
        except Exception as e:
            logging.error(f"Error during search: {e}")
            return [{"error": f"Error during search: {str(e)}"}]
    
    def fetch_and_summarize(self, url):
        """
        Fetch a URL and provide a summary of its content.
        
        Args:
            url (str): URL to fetch and summarize
            
        Returns:
            dict: Summary information
        """
        # Fetch the URL
        success, content = self.fetch_url(url)
        
        if not success:
            return {"error": content}
        
        try:
            # Parse as article
            article = self.parse_article(content, url)
            
            # Create a more detailed summary
            if article["content"]:
                # Get first few paragraphs (up to 300 words)
                paragraphs = article["content"].split('\n\n')
                summary_text = "\n\n".join(paragraphs[:3])
                
                words = summary_text.split()
                if len(words) > 300:
                    summary_text = " ".join(words[:300]) + "..."
                
                article["summary"] = summary_text
            
            return {
                "url": url,
                "title": article["title"],
                "author": article["author"],
                "date": article["date"],
                "summary": article["summary"]
            }
            
        except Exception as e:
            logging.error(f"Error summarizing content: {e}")
            return {"error": f"Error summarizing content: {str(e)}"}
    
    def _is_url_safe(self, url):
        """
        Check if a URL is safe to fetch.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if safe, False otherwise
        """
        # Check if it's a proper URL
        if not url or not isinstance(url, str):
            return False
        
        # Check URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Only allow HTTP and HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Check for potentially dangerous extensions
        if any(parsed.path.endswith(ext) for ext in ['.exe', '.zip', '.rar', '.msi', '.bat', '.sh']):
            return False
        
        # Check for allowed domains (optional)
        allowed_domains = Config.get("allowed_domains", [])
        if allowed_domains and parsed.netloc not in allowed_domains:
            logging.warning(f"Domain not in allowed list: {parsed.netloc}")
            # Don't block, just warn
        
        # Block certain domains (e.g., known malicious sites)
        blocked_domains = Config.get("blocked_domains", [])
        if blocked_domains and parsed.netloc in blocked_domains:
            return False
        
        return True