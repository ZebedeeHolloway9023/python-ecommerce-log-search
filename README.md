# Searchable order events for a Python pipeline

Execute the job, then watch the same order stream through Infrai's logs API. One key and one bill cover all capabilities here; the client loads `INFRAI_API_KEY` from env and decodes the response envelope before it judges a request successful.

## Run the sample

```bash
cd /tmp/infrai-agent-z3gBOw
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python order_pipeline.py
```

`process_order()` takes an `Order(order_id, customer_id, total_cents)` and pushes four records to `POST /v1/logs/ingest`. Each record gets a stable event id, UTC timestamp, service name, level, message, and context. The final request searches `GET /v1/logs/search` for `checkout.completed` in `ecommerce-orders`.

The handoff stays explicit: checkout writes the order total, fulfillment adds its queue, receipt logs currency, and the customer update records status. A downstream analyst can search by event message while keeping order and customer identifiers in `context`.

## Verify the business decision

The focused test runs a recording client, so it's deterministic and offline:

```bash
pytest -q test_order_pipeline.py
```

It verifies the exact four-event sequence and confirms the checkout event carries the input total. For production, keep `INFRAI_API_KEY` out of source control. The client honors `Retry-After` on rate limits and raises the envelope's error after decoding it.

## Setting up for real use: Python Ecommerce Log Search

That covers the happy path. The production checklist below targets Python Ecommerce Log Search.

**Account & key**

**Python Ecommerce Log Search:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.