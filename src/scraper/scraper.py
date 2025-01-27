import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import asyncio
from datetime import datetime

class TUMScraper:
    def __init__(self):
        self.base_url = "https://portal.fis.tum.de/en/publications/"
        self.logger = logging.getLogger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def fetch_publications(self) -> List[Dict]:
        try:
            publications = []
            page = 1
            while True:
                page_publications = await self._fetch_page(page)
                if not page_publications:
                    break
                publications.extend(page_publications)
                page += 1
                await asyncio.sleep(1)  # Polite delay between pages
            
            self.logger.info(f"Successfully scraped {len(publications)} publications")
            return publications
            
        except Exception as e:
            self.logger.error(f"Error fetching publications: {e}")
            return []

    async def _fetch_page(self, page: int) -> List[Dict]:
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                url = f"{self.base_url}?page={page}"
                async with session.get(url) as response:
                    response.raise_for_status()
                    html = await response.text()
                    
            soup = BeautifulSoup(html, 'html.parser')
            publications = []
            
            # Find the main publications container
            pub_container = soup.find('div', class_='publications-list')
            if not pub_container:
                return []

            # Process each publication entry
            for pub_div in pub_container.find_all('div', class_='publication-item'):
                try:
                    publication = {
                        'title': self._extract_text(pub_div.find('h3', class_='title')),
                        'authors': self._extract_authors(pub_div.find('div', class_='authors')),
                        'abstract': self._extract_text(pub_div.find('div', class_='abstract')),
                        'publication_date': self._parse_date(
                            self._extract_text(pub_div.find('span', class_='date'))
                        ),
                        'department': self._extract_text(pub_div.find('div', class_='department')),
                        'url': self._extract_url(pub_div.find('a', class_='publication-link')),
                        'doi': self._extract_doi(pub_div),
                        'publication_type': self._extract_text(pub_div.find('span', class_='type')),
                        'scraped_at': datetime.utcnow().isoformat(),
                    }
                    
                    if self._is_valid_publication(publication):
                        publications.append(publication)
                        
                except Exception as e:
                    self.logger.error(f"Error processing publication: {e}")
                    continue
            
            return publications
            
        except Exception as e:
            self.logger.error(f"Error fetching page {page}: {e}")
            return []

    def _extract_text(self, element) -> str:
        return element.get_text(strip=True) if element else ""
    
    def _extract_authors(self, authors_div) -> List[str]:
        if not authors_div:
            return []
        # Handle different author formats (comma-separated, semicolon-separated, etc.)
        text = authors_div.get_text(strip=True)
        authors = []
        for separator in [';', ',']:
            if separator in text:
                authors = [author.strip() for author in text.split(separator)]
                break
        if not authors:
            authors = [text]
        return [author for author in authors if author]

    def _extract_url(self, link_element) -> str:
        if not link_element:
            return ""
        url = link_element.get('href', '')
        if url and not url.startswith(('http://', 'https://')):
            url = f"https://portal.fis.tum.de{url}"
        return url

    def _extract_doi(self, pub_div) -> str:
        doi_element = pub_div.find('span', class_='doi')
        if doi_element:
            doi_text = self._extract_text(doi_element)
            # Extract DOI from text like "DOI: 10.1234/abcd"
            return doi_text.replace('DOI:', '').strip()
        return ""

    def _parse_date(self, date_str: str) -> str:
        try:
            # Handle different date formats
            for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%B %d, %Y']:
                try:
                    return datetime.strptime(date_str.strip(), fmt).isoformat()
                except ValueError:
                    continue
            return date_str
        except Exception:
            return date_str

    def _is_valid_publication(self, publication: Dict) -> bool:
        """Check if the publication has the minimum required fields"""
        required_fields = ['title', 'authors']
        return all(publication.get(field) for field in required_fields) 