import json
import boto3
import random
import string
from decimal import Decimal
from urllib.parse import urlparse

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('URLShortener')

# Function to convert Decimal values to int
def decimal_to_int(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    return obj

def lambda_handler(event, context):
    print("DEBUG: Received event:", json.dumps(event, indent=2))  # Debugging log

    http_method = event.get('httpMethod', '')

    if http_method == "POST":
        if 'body' not in event or event['body'] is None:
            return {"statusCode": 400, "body": json.dumps({"error": "Request body is missing"})}

        body = json.loads(event['body'])
        original_url = body.get('url')
        custom_code = body.get('custom_code', None)

        if not original_url or not urlparse(original_url).scheme:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid URL"})}

        if custom_code:
            response = table.get_item(Key={"short_code": custom_code})
            if 'Item' in response:
                return {"statusCode": 400, "body": json.dumps({"error": "Custom code already in use"})}
            short_code = custom_code
        else:
            while True:
                short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                response = table.get_item(Key={"short_code": short_code})
                if 'Item' not in response:
                    break

        table.put_item(Item={"short_code": short_code, "original_url": original_url, "clicks": 0})

        return {
            "statusCode": 200,
            "body": json.dumps({"short_url": f"https://nx6zi5w8di.execute-api.eu-central-1.amazonaws.com/prod/{short_code}"})
        }

    elif http_method == "GET":
        # Handling Redirection
        if 'pathParameters' in event and event['pathParameters'] and 'short_code' in event['pathParameters']:
            short_code = event['pathParameters']['short_code']
            print(f"DEBUG: Redirect request for short_code: {short_code}")

            response = table.get_item(Key={"short_code": short_code})
            print("DEBUG: DynamoDB response:", response)

            item = response.get('Item')

            if not item:
                print(f"DEBUG: No item found for {short_code}")
                return {"statusCode": 404, "body": json.dumps({"error": "Short URL not found"})}

            # Increment click count
            table.update_item(
                Key={"short_code": short_code},
                UpdateExpression="SET clicks = clicks + :inc",
                ExpressionAttributeValues={":inc": 1}
            )

            return {
                "statusCode": 302,
                "headers": {"Location": item['original_url']}
            }

    return {"statusCode": 400, "body": json.dumps({"error": "Unsupported HTTP method"})}
