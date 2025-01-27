import json
import asyncio
from main import process_publications
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        # Run the async process_publications function
        asyncio.run(process_publications())
        
        return {
            'statusCode': 200,
            'body': json.dumps('Publications processed successfully')
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing publications: {str(e)}')
        } 