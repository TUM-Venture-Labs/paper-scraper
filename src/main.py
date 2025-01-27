import asyncio
import schedule
import time
from scraper.scraper import TUMScraper
from database.supabase_client import SupabaseClient
from gpt.analyzer import PublicationAnalyzer
from notifications.notification import NotificationManager
import logging
from typing import List, Dict
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_publications():
    try:
        scraper = TUMScraper()
        db_client = SupabaseClient()
        analyzer = PublicationAnalyzer()
        notifier = NotificationManager()

        # Fetch publications
        publications = await scraper.fetch_publications()
        logger.info(f"Fetched {len(publications)} publications")
        
        # Process each publication
        for pub in publications:
            # Analyze the publication
            analysis = await analyzer.analyze_publication(pub)
            if analysis:
                # Store in database
                stored_pub = await db_client.store_publication(pub)
                
                # Send notifications if needed
                await notifier.process_publication_analysis(pub, analysis)
                
            await asyncio.sleep(1)  # Rate limiting
            
    except Exception as e:
        logger.error(f"Error in process_publications: {e}")

def run_scheduler():
    logger.info("Starting scheduler")
    
    # Schedule weekly runs
    schedule.every().monday.at("00:00").do(lambda: asyncio.run(process_publications()))
    
    # Also allow manual runs
    if os.getenv("RUN_IMMEDIATELY", "false").lower() == "true":
        asyncio.run(process_publications())
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    load_dotenv()
    run_scheduler() 