# AWS Lambda URL Shortener 🚀

This is a simple URL shortener using **AWS Lambda, API Gateway, and DynamoDB**.

## Features
- Shortens long URLs
- Redirects using the short code
- Uses AWS services (Lambda, API Gateway, DynamoDB)

## API Endpoints
- `POST /shorten` - Create a short URL
- `GET /{short_code}` - Redirect to the original URL

## How to Deploy
- Deploy the Lambda function
- Connect it to API Gateway
- Use DynamoDB for storing URLs
