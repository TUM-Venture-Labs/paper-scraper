# Paper Scraper

A tool that scrapes publications from TUM's research portal (https://portal.fis.tum.de/en/publications/) and processes them using AI to identify potential startup opportunities.

## Features

- Weekly automated scraping of TUM publications
- Storage of publication data in Supabase
- AI-powered analysis of practical applicability
- Identification of startup potential
- Automated deployment to AWS Lambda
- GitHub Actions for CI/CD

## Project Structure

- `scraper/`: Contains the web scraping logic
- `database/`: Database connection and models
- `gpt/`: GPT-based analysis of publications
- `utils/`: Helper functions and utilities
- `.github/workflows/`: GitHub Actions for CI/CD

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/paper-scraper.git
   cd paper-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` for local development
   - Set up GitHub repository secrets for deployment

4. Local development:
   ```bash
   python src/main.py
   ```

## Deployment

The application is automatically deployed to AWS Lambda when pushing to the main branch.

### Manual Deployment

1. Install Serverless Framework:
   ```bash
   npm install -g serverless
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

3. Deploy:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## GitHub Actions

The repository includes GitHub Actions for:
- Automated testing on pull requests
- Deployment to AWS Lambda on merge to main
- Weekly scheduled runs

## Required GitHub Secrets

Set up the following secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `OPENAI_API_KEY`
- `SLACK_WEBHOOK_URL`
- `EMAIL_ENABLED`
- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`

## License

MIT