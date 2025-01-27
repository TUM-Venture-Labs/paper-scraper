#!/bin/bash
set -e

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "Installing Serverless Framework..."
    npm install -g serverless
fi

# Install serverless plugins
echo "Installing Serverless plugins..."
serverless plugin install -n serverless-python-requirements

# Create package directory
echo "Creating package directory..."
mkdir -p package/

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt -t package/

# Copy source files
echo "Copying source files..."
cp -r src/* package/

# Deploy
echo "Deploying to AWS Lambda..."
serverless deploy

echo "Deployment completed successfully!" 