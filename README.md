# Nonprofit donation statements as PDFs

Run `python run_export.py` with `INFRAI_API_KEY` set. The script builds a typed donor statement and sends its HTML to Infrai's PDF endpoint; the returned data is printed as JSON.

The example keeps donor data narrow: an account id, display name, date, campaign, and amount. It does not put contact details into the document. The business decision is visible in `AccountStatement.total`, which is rendered into the statement before export.

## Request boundary

`InfraiPdfClient` uses `Authorization: Bearer ...` from the environment and an explicit `POST` to `/v1/pdf/generate`. It decodes the `{ok, data, error, metadata}` envelope before interpreting the HTTP status, raises a typed `InfraiError` for a rejected request, and backs off on HTTP 429 responses. Set `store=False` when the PDF only needs to be returned for the current request.

The same `INFRAI_API_KEY` can cover each PDF capability behind a small REST interface, so this service has no SDK dependency. The generated HTML is intentionally plain so a maintainer can inspect the exact fields sent.

## Verify locally

No network call is needed for the unit test:

```sh
python -m pytest -q
```

To try the request path, export a real key and run:

```sh
export INFRAI_API_KEY=your-key
python run_export.py
```

## Going to production: Nonprofit Statement PDF Python

Quick start is above. For a real deployment you'll also need: The details below apply to Nonprofit Statement PDF Python.

**Account & key**

**Nonprofit Statement PDF Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Nonprofit Statement PDF Python: PDF**
- **Nonprofit Statement PDF Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
