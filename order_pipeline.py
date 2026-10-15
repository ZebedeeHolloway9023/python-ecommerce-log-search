from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from infrai_logs import LogsClient


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    total_cents: int


def process_order(order: Order, client: LogsClient) -> list[dict]:
    """Emit the four records an analytics pipeline needs for one order."""
    events = [
        ("checkout.completed", {"total_cents": order.total_cents}),
        ("fulfillment.queued", {"queue": "standard"}),
        ("receipt.issued", {"currency": "USD"}),
        ("customer.order_updated", {"status": "processing"}),
    ]
    sent = []
    for event_name, details in events:
        record = {
            "id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "ecommerce-orders",
            "level": "info",
            "message": event_name,
            "context": {"order_id": order.order_id, "customer_id": order.customer_id, **details},
        }
        sent.append(client.ingest(record))
    return sent


if __name__ == "__main__":
    client = LogsClient()
    order = Order("ord-1042", "cus-88", 1299)
    process_order(order, client)
    print(client.search("checkout.completed", "ecommerce-orders"))
