import json
import boto3
import random
import string
from urllib.parse import urlparse

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('URLShortener')

# Function to generate a short random string
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))  # Debugging

    # Ensure 'httpMethod' exists
    http_method = event.get('httpMethod', '')

    if http_method == "POST":
        if 'body' not in event or event['body'] is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Request body is missing"})
            }

        body = json.loads(event['body'])
        original_url = body.get('url')

        if not original_url or not urlparse(original_url).scheme:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid URL"})
            }

        short_code = generate_short_code()

        table.put_item(Item={"short_code": short_code, "original_url": original_url})

        return {
            "statusCode": 200,
            "body": json.dumps({"short_url": f"https://your-api-gateway-url/prod/{short_code}"})
        }

    elif http_method == "GET":
        # Make sure pathParameters exist
        if 'pathParameters' not in event or not event['pathParameters']:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing path parameter"})
            }

        short_code = event['pathParameters'].get('short_code')
        if not short_code:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Short code is missing"})
            }

        response = table.get_item(Key={"short_code": short_code})
        item = response.get('Item')

        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Short URL not found"})
            }

        return {
            "statusCode": 302,
            "headers": {"Location": item['original_url']}
        }

    return {
        "statusCode": 400,
        "body": json.dumps({"error": "Unsupported HTTP method"})
    }
