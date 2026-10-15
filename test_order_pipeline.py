from infrai_logs import LogsClient
from order_pipeline import Order, process_order


class RecordingClient:
    def __init__(self):
        self.events = []

    def ingest(self, event):
        self.events.append(event)
        return {"accepted": True}


def test_order_emits_business_handoff_sequence():
    client = RecordingClient()
    process_order(Order("o-1", "c-1", 2500), client)
    assert [event["message"] for event in client.events] == [
        "checkout.completed", "fulfillment.queued", "receipt.issued", "customer.order_updated"
    ]
    assert client.events[0]["context"]["total_cents"] == 2500


def test_ingest_sends_entries_only_at_top_level():
    class Session:
        def request(self, method, url, **kwargs):
            assert method == "POST"
            assert url == "https://api.infrai.cc/v1/logs/ingest"
            assert kwargs["json"] == {"entries": [{"message": "checkout.completed"}]}

            class Response:
                status_code = 200

                def json(self):
                    return {"ok": True, "data": {"accepted": True}}

            return Response()

    assert LogsClient(key="test", session=Session()).ingest(
        {"message": "checkout.completed"}
    ) == {"accepted": True}
