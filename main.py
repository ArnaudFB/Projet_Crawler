import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import time
from urllib.robotparser import RobotFileParser


class WebCrawler:
    def __init__(self, start_url, max_pages):
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited_urls = set()
        self.results = []
        self.robot_parser = self.init_robot_parser()

    def init_robot_parser(self):
        """Initialize and parse robots.txt."""
        parsed_url = urlparse(self.start_url)
        robots_url = urljoin(f"{parsed_url.scheme}://{parsed_url.netloc}", "/robots.txt")
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception as e:
            print(f"Failed to fetch robots.txt: {e}")
        return rp

    def is_allowed_by_robots(self, url):
        """Check if a URL is allowed to be crawled based on robots.txt."""
        return self.robot_parser.can_fetch("*", url)

    def is_valid_url(self, url):
        """Check if the URL is valid and within the same domain."""
        parsed_start = urlparse(self.start_url)
        parsed_url = urlparse(url)
        return parsed_url.netloc == parsed_start.netloc and url not in self.visited_urls

    def fetch_page(self, url):
        """Fetch the content of a URL."""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; Crawler/1.0)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_page(self, html, url):
        """Parse the HTML content of a page and extract relevant information."""
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        first_paragraph = soup.find('p').text if soup.find('p') else "No Content"
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        product_links = [link for link in links if "product" in link]

        return {
            "title": title,
            "url": url,
            "first_paragraph": first_paragraph,
            "relevant_links": product_links
        }

    def crawl(self):
        """Main crawling logic."""
        to_visit = [self.start_url]

        while to_visit and len(self.visited_urls) < self.max_pages:
            current_url = to_visit.pop(0)

            if current_url in self.visited_urls or not self.is_allowed_by_robots(current_url):
                continue

            print(f"Visiting: {current_url}")
            html = self.fetch_page(current_url)
            if not html:
                continue

            data = self.parse_page(html, current_url)
            self.results.append(data)
            self.visited_urls.add(current_url)

            for link in data["relevant_links"]:
                if self.is_valid_url(link):
                    to_visit.append(link)

            time.sleep(1)  # Politeness delay

        self.save_results()

    def save_results(self):
        """Save the results to a JSON file."""
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    START_URL = "https://web-scraping.dev/products"
    MAX_PAGES = 50

    crawler = WebCrawler(START_URL, MAX_PAGES)
    crawler.crawl()