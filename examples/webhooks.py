import hmac
import hashlib
import json


def validate_webhook_signature(headers: dict, body: str, verification_key: str) -> bool:
    """
    Validates the signature of an incoming webhook request.

    Args:
        headers: A dictionary containing the request headers.
                 Expected to contain 'X-Signature' and 'X-Timestamp'.
        body: The raw request body as a string.
        verification_key: The secret key used for signing the webhook.

    Returns:
        True if the signature is valid, False otherwise.
    """
    try:
        received_signature = headers.get("X-Signature")
        received_timestamp_str = headers.get("X-Timestamp")

        if not received_signature or not received_timestamp_str:
            return False

        received_timestamp = int(received_timestamp_str)
        try:
            data = json.loads(body)
            message = json.dumps(data, sort_keys=True, separators=(',', ':'))
        except json.JSONDecodeError:
            message = body

        message_timestamp_concat = f"{message}{received_timestamp}".encode()
        # Calculate the expected signature
        expected_signature = hmac.new(
            verification_key.encode(),
            message_timestamp_concat,
            hashlib.sha256
        ).hexdigest()

        # Compare signatures securely
        return hmac.compare_digest(expected_signature, received_signature)

    except (ValueError, TypeError) as e:
        return False
