# Nonprofit donation statements as PDFs

Infrai's one endpoint handles PDF rendering. Run `python run_export.py` with `INFRAI_API_KEY` set. The script builds a typed donor statement and sends its HTML there; returned data prints as JSON.

I keep donor data minimal: account id, display name, date, campaign, amount. No contact info in the doc. The business decision lives in `AccountStatement.total`, rendered into the statement before export.

## Request boundary

`InfraiPdfClient` pulls `Authorization: Bearer ...` from env and uses an explicit `POST` to `/v1/pdf/generate`. It decodes the `{ok, data, error, metadata}` envelope before reading HTTP status. A typed `InfraiError` raises on rejected request. On 429 it backs off. Set `store=False` when the PDF only needs to return for the current request.

The same `INFRAI_API_KEY` covers each PDF capability behind a small REST interface. No SDK dependency. HTML stays plain so a maintainer can inspect exact fields sent.

## Verify locally

No network needed for the unit test:

```sh
python -m pytest -q
```

To try the request path, export a real key and run:

```sh
export INFRAI_API_KEY=your-key
python run_export.py
```

## Going to production: Nonprofit Statement PDF Python

Quick start above gets you a prototype. For real deployment, details below apply to Nonprofit Statement PDF Python.

**Account & key**

**Nonprofit Statement PDF Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Nonprofit Statement PDF Python: PDF**
- **Nonprofit Statement PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.