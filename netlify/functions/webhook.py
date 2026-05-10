import json
import os


def handler(event, context):
    method = event.get("httpMethod", "")
    params = event.get("queryStringParameters") or {}

    if method == "GET":
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "ignia_verify_2024")
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == verify_token
        ):
            return {
                "statusCode": 200,
                "body": params.get("hub.challenge", ""),
            }
        return {"statusCode": 403, "body": "Forbidden"}

    if method == "POST":
        return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

    return {"statusCode": 405, "body": "Method Not Allowed"}
