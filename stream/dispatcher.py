import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

import pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://guest:guest@localhost:5672/%2F"
)

EXCHANGE = "rapido-dispatch"
INTERVAL_SECONDS = 2

ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "adyar", "velachery"],
}

TYPES = ["ride", "food"]


def main():
    connection = pika.BlockingConnection(
        pika.URLParameters(RABBITMQ_URL)
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True,
    )

    count = 0

    print(f"Dispatcher connected. Exchange: {EXCHANGE}")
    print("Publishing every 2 seconds. Every 10th message is malformed.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            count += 1

            city = random.choice(list(ZONES.keys()))
            zone = random.choice(ZONES[city])
            request_type = random.choice(TYPES)

            # Keep the routing key valid even for malformed payloads.
            routing_key = f"{city}.{zone}.{request_type}"

            message = {
                "id": str(uuid.uuid4())[:8],
                "city": city,
                "type": request_type,
                "ts": datetime.now(timezone.utc).isoformat(),
            }

            if count % 10 != 0:
                message["zone"] = zone
                status = "VALID"
            else:
                status = "MALFORMED - zone missing"

            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )

            print(
                f"[{status}] #{count} "
                f"key={routing_key} "
                f"message={json.dumps(message)}"
            )

            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nDispatcher stopping...")
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()