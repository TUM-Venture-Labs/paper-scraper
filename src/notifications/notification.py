import os
from typing import Dict, Optional, List
import logging
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

class NotificationManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")
        self.score_threshold = float(os.getenv("SCORE_THRESHOLD", "7.0"))  # Default threshold of 7.0
        self.notification_channels = self._load_notification_channels()

    def _load_notification_channels(self) -> Dict:
        """Load notification channel configurations"""
        return {
            'slack': {
                'enabled': os.getenv("SLACK_ENABLED", "false").lower() == "true",
                'webhook_url': os.getenv("SLACK_WEBHOOK_URL"),
            },
            'email': {
                'enabled': os.getenv("EMAIL_ENABLED", "false").lower() == "true",
                'smtp_server': os.getenv("SMTP_SERVER"),
                'smtp_port': os.getenv("SMTP_PORT"),
                'smtp_user': os.getenv("SMTP_USER"),
                'smtp_password': os.getenv("SMTP_PASSWORD"),
                'from_email': os.getenv("FROM_EMAIL"),
                'to_email': os.getenv("TO_EMAIL"),
            }
        }

    async def process_publication_analysis(self, publication_data: Dict, analysis_result: Dict) -> None:
        """Process a publication analysis and send notifications if needed"""
        try:
            score = float(analysis_result.get('startup_potential_score', 0))
            
            if score >= self.score_threshold:
                await self._send_high_potential_notification(publication_data, analysis_result)
                self.logger.info(f"Sent notification for high-potential publication: {publication_data['title']}")
                
        except Exception as e:
            self.logger.error(f"Error processing publication analysis: {e}")

    async def _send_high_potential_notification(self, publication: Dict, analysis: Dict) -> None:
        """Send notifications through configured channels"""
        notification_data = self._prepare_notification_data(publication, analysis)
        
        # Send to all enabled channels
        tasks = []
        if self.notification_channels['slack']['enabled']:
            tasks.append(self._send_slack_notification(notification_data))
        if self.notification_channels['email']['enabled']:
            tasks.append(self._send_email_notification(notification_data))
            
        await asyncio.gather(*tasks)

    def _prepare_notification_data(self, publication: Dict, analysis: Dict) -> Dict:
        """Prepare notification data in a structured format"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'publication': {
                'title': publication.get('title'),
                'authors': publication.get('authors', []),
                'department': publication.get('department'),
                'url': publication.get('url'),
                'publication_date': publication.get('publication_date')
            },
            'analysis': {
                'score': analysis.get('startup_potential_score'),
                'summary': analysis.get('detailed_analysis', {}).get('summary'),
                'key_metrics': analysis.get('key_metrics', {}),
                'recommendations': analysis.get('recommendations', {})
            },
            'contact_info': self._get_sanitized_contact_info(publication)
        }

    def _get_sanitized_contact_info(self, publication: Dict) -> Dict:
        """Get sanitized contact information respecting privacy preferences"""
        contact_info = {}
        
        # Only include contact methods that researchers have explicitly agreed to share
        if publication.get('contact_consent', False):
            if publication.get('public_email'):
                contact_info['email'] = publication['public_email']
            if publication.get('public_phone'):
                contact_info['phone'] = publication['public_phone']
            if publication.get('department_contact'):
                contact_info['department'] = publication['department_contact']
                
        return contact_info

    async def _send_slack_notification(self, notification_data: Dict) -> None:
        """Send notification to Slack"""
        try:
            webhook_url = self.notification_channels['slack']['webhook_url']
            if not webhook_url:
                raise ValueError("Slack webhook URL not configured")

            message = self._format_slack_message(notification_data)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    response.raise_for_status()
                    
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")

    def _format_slack_message(self, data: Dict) -> Dict:
        """Format notification data for Slack"""
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚀 High-Potential Publication Detected!"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Title:*\n{data['publication']['title']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Score:*\n{data['analysis']['score']}/10"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{data['analysis']['summary']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Department:*\n{data['publication']['department']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time to Market:*\n{data['analysis']['key_metrics'].get('estimated_time_to_market', 'N/A')} months"
                        }
                    ]
                }
            ]
        }

    async def _send_email_notification(self, notification_data: Dict) -> None:
        """Send notification via email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            config = self.notification_channels['email']
            
            message = MIMEMultipart()
            message["From"] = config['from_email']
            message["To"] = config['to_email']
            message["Subject"] = f"High-Potential Publication Alert: {notification_data['publication']['title']}"
            
            body = self._format_email_body(notification_data)
            message.attach(MIMEText(body, "html"))
            
            with smtplib.SMTP(config['smtp_server'], int(config['smtp_port'])) as server:
                server.starttls()
                server.login(config['smtp_user'], config['smtp_password'])
                server.send_message(message)
                
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")

    def _format_email_body(self, data: Dict) -> str:
        """Format notification data as HTML email"""
        return f"""
        <html>
            <body>
                <h2>🚀 High-Potential Publication Detected</h2>
                <h3>Publication Details</h3>
                <p><strong>Title:</strong> {data['publication']['title']}</p>
                <p><strong>Authors:</strong> {', '.join(data['publication']['authors'])}</p>
                <p><strong>Department:</strong> {data['publication']['department']}</p>
                <p><strong>Score:</strong> {data['analysis']['score']}/10</p>
                
                <h3>Analysis Summary</h3>
                <p>{data['analysis']['summary']}</p>
                
                <h3>Key Metrics</h3>
                <ul>
                    <li>Time to Market: {data['analysis']['key_metrics'].get('estimated_time_to_market', 'N/A')} months</li>
                    <li>Investment Level: {data['analysis']['key_metrics'].get('required_investment_level', 'N/A')}</li>
                    <li>Risk Level: {data['analysis']['key_metrics'].get('risk_level', 'N/A')}</li>
                </ul>
                
                <h3>Next Steps</h3>
                <ul>
                    {''.join(f'<li>{step}</li>' for step in data['analysis']['recommendations'].get('next_steps', []))}
                </ul>
                
                <p><a href="{data['publication']['url']}">View Publication</a></p>
            </body>
        </html>
        """
