import json
import time
import requests


class NewRelicLogger:
    US_ENDPOINT = "https://log-api.newrelic.com/log/v1"
    EU_ENDPOINT = "https://log-api.eu.newrelic.com/log/v1"

    def __init__(self, api_key, service_name="default-service", region="US"):
        self.api_key = api_key
        self.service_name = service_name
        self.endpoint = self.EU_ENDPOINT if region.upper() == "EU" else self.US_ENDPOINT

    def send_log(self, message, level="INFO", attributes=None):
        payload = [
            {
                "common": {
                    "attributes": {
                        "service": self.service_name,
                        "logtype": "application",
                    }
                },
                "logs": [
                    {
                        "timestamp": int(time.time() * 1000),
                        "message": message,
                        "attributes": {
                            "level": level,
                            **(attributes or {}),
                        },
                    }
                ],
            }
        ]

        response = requests.post(
            self.endpoint,
            headers={
                "Api-Key": self.api_key,
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        return response.status_code, response.text

    def send_batch(self, logs):
        """
        logs: list of dicts with keys: message, level (optional), attributes (optional)
        """
        log_entries = []
        for log in logs:
            log_entries.append(
                {
                    "timestamp": int(time.time() * 1000),
                    "message": log["message"],
                    "attributes": {
                        "level": log.get("level", "INFO"),
                        **log.get("attributes", {}),
                    },
                }
            )

        payload = [
            {
                "common": {
                    "attributes": {
                        "service": self.service_name,
                        "logtype": "application",
                    }
                },
                "logs": log_entries,
            }
        ]

        response = requests.post(
            self.endpoint,
            headers={
                "Api-Key": self.api_key,
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )
        return response.status_code, response.text


# Usage
if __name__ == "__main__":
    logger = NewRelicLogger(
        api_key="YOUR_NEW_RELIC_LICENSE_KEY",
        service_name="primevault-api",
        region="US",
    )

    # Single log
    status, body = logger.send_log(
        message="User login successful",
        level="INFO",
        attributes={"userId": "abc-123", "action": "login"},
    )
    print(f"Status: {status}, Response: {body}")

    # Batch logs
    status, body = logger.send_batch(
        [
            {"message": "Transaction created", "level": "INFO", "attributes": {"txId": "tx-001"}},
            {"message": "Transaction failed", "level": "ERROR", "attributes": {"txId": "tx-002", "error": "insufficient funds"}},
        ]
    )
    print(f"Status: {status}, Response: {body}")
