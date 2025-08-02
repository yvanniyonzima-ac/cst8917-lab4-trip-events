import json
import random
import asyncio
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from datetime import datetime

# Replace with your Event Hubs connection string
CONNECTION_STR = "Endpoint=sb://dispatch-system.servicebus.windows.net/;SharedAccessKeyName=SendPolicy;SharedAccessKey=l8iuJbIZgfTLEwMTGHyc4MFl7yG+Q5m0++AEhHYC+2E="
EVENTHUB_NAME = "taxitripevents"

def generate_trip_event():
    vendor_ids = ["1", "2", "3", "4"]
    payment_types = ["1", "2", "3"]  # 1=Credit Card, 2=Cash, 3=No Charge

    vendor_id = random.choice(vendor_ids)
    trip_distance = round(random.uniform(0.5, 20.0), 2)
    passenger_count = random.randint(1, 6)
    payment_type = random.choice(payment_types)

    # Introduce interesting patterns
    if random.random() < 0.15:
        passenger_count = random.randint(5, 7)
    if random.random() < 0.10:
        payment_type = "2"
        trip_distance = round(random.uniform(0.1, 0.9), 2)
    if random.random() < 0.05:
        payment_type = "2"
        trip_distance = round(random.uniform(15.0, 30.0), 2)

    return {
        "vendorID": vendor_id,
        "tripDistance": trip_distance,
        "passengerCount": passenger_count,
        "paymentType": payment_type,
        "pickupTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tripID": str(random.randint(100000, 999999))
    }

async def send_events():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME
    )

    try:
        while True:
            event_data_batch = await producer.create_batch()
            for _ in range(random.randint(1, 5)):
                trip = generate_trip_event()
                event_data_batch.add(EventData(json.dumps({"ContentData": trip})))
                print(f"Sending event: {json.dumps(trip)}")

            await producer.send_batch(event_data_batch)
            print(f"✅ Sent batch of {len(event_data_batch)} events.")
            await asyncio.sleep(random.uniform(1, 3))
    finally:
        await producer.close()

if __name__ == "__main__":
    asyncio.run(send_events())
