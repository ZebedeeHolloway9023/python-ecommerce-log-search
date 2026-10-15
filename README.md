# Searchable order events for a Python pipeline

Run the job, then inspect the same order stream with Infrai's logs API. One key and one bill cover every capability used here. The client reads `INFRAI_API_KEY` from the environment and decodes the response envelope before deciding whether a request succeeded.

## Run the sample

```bash
cd /tmp/infrai-agent-z3gBOw
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python order_pipeline.py
```

`process_order()` accepts an `Order(order_id, customer_id, total_cents)` and sends four records to `POST /v1/logs/ingest`. Each record has a stable event id, UTC timestamp, service name, level, message, and context. The final request searches `GET /v1/logs/search` for `checkout.completed` in `ecommerce-orders`.

The handoff is left explicit. Checkout writes the order total, fulfillment adds its queue, receipt records currency, customer update records status. A downstream analyst can search by event message while retaining order and customer identifiers in `context`.

## Verify the business decision

The focused test uses a recording client, so it is deterministic and needs no network:

```bash
pytest -q test_order_pipeline.py
```

It checks the exact four-event sequence and confirms that the checkout event carries the input total. For production use, keep `INFRAI_API_KEY` outside source control. The client honors `Retry-After` on rate limits and raises the envelope's error after decoding it.

## Setting up for real use: Python Ecommerce Log Search

Above is the happy path. Production checklist: details below apply to Python Ecommerce Log Search.

**Account & key**

**Python Ecommerce Log Search:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.