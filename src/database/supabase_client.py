from supabase import create_client
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List
import logging
from datetime import datetime

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not all([supabase_url, supabase_key]):
            raise ValueError("Missing Supabase credentials in environment variables")
            
        self.client = create_client(supabase_url, supabase_key)

    async def store_publication(self, publication_data: Dict) -> Optional[Dict]:
        try:
            # Check if publication already exists
            existing = await self._find_existing_publication(publication_data)
            if existing:
                self.logger.info(f"Publication already exists: {publication_data['title']}")
                return existing

            # Store the publication
            response = await self.client.table('publications').insert({
                'title': publication_data['title'],
                'authors': publication_data['authors'],
                'abstract': publication_data.get('abstract', ''),
                'publication_date': publication_data.get('publication_date', ''),
                'department': publication_data.get('department', ''),
                'url': publication_data.get('url', ''),
                'doi': publication_data.get('doi', ''),
                'publication_type': publication_data.get('publication_type', ''),
                'scraped_at': datetime.utcnow().isoformat(),
                'processed': False
            }).execute()
            
            self.logger.info(f"Successfully stored publication: {publication_data['title']}")
            return response.data[0]
            
        except Exception as e:
            self.logger.error(f"Error storing publication: {e}")
            return None

    async def _find_existing_publication(self, publication_data: Dict) -> Optional[Dict]:
        """Check if publication already exists using DOI or title+authors"""
        try:
            if publication_data.get('doi'):
                response = await self.client.table('publications').select('*').eq('doi', publication_data['doi']).execute()
                if response.data:
                    return response.data[0]

            # If no DOI or not found by DOI, check title and authors
            response = await self.client.table('publications').select('*').eq('title', publication_data['title']).execute()
            if response.data:
                stored_authors = set(response.data[0]['authors'])
                new_authors = set(publication_data['authors'])
                if stored_authors.intersection(new_authors):
                    return response.data[0]

            return None
        except Exception as e:
            self.logger.error(f"Error checking existing publication: {e}")
            return None

    async def mark_as_processed(self, publication_id: str) -> bool:
        try:
            await self.client.table('publications').update({
                'processed': True,
                'processed_at': datetime.utcnow().isoformat()
            }).eq('id', publication_id).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error marking publication as processed: {e}")
            return False 