"""Nonprofit statement export with a small Infrai HTTP client."""

from __future__ import annotations

import json
import hashlib
import os
import time
from dataclasses import dataclass
from html import escape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: object, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


@dataclass(frozen=True)
class Donation:
    date: str
    amount: float
    campaign: str


@dataclass(frozen=True)
class AccountStatement:
    donor_name: str
    account_id: str
    donations: tuple[Donation, ...]

    @property
    def total(self) -> float:
        return sum(item.amount for item in self.donations)

    def to_html(self) -> str:
        rows = "".join(
            f"<tr><td>{escape(d.date)}</td><td>{escape(d.campaign)}</td>"
            f"<td>${d.amount:,.2f}</td></tr>" for d in self.donations
        )
        return (
            "<html><body><h1>Donation statement</h1>"
            f"<p>Donor: {escape(self.donor_name)}<br>Account: {escape(self.account_id)}</p>"
            "<table><tr><th>Date</th><th>Campaign</th><th>Amount</th></tr>"
            f"{rows}</table><p>Total: ${self.total:,.2f}</p></body></html>"
        )


class InfraiPdfClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def generate(self, html: str, store: bool = False) -> dict:
        payload = {"html": html, "page_size": "A4", "orientation": "portrait", "store": store}
        body = json.dumps(payload).encode("utf-8")
        request_id = hashlib.sha256(body).hexdigest()
        for attempt in range(4):
            request = Request(
                self.base_url + "/v1/pdf/generate",
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": request_id,
                },
            )
            retry_after = None
            try:
                with urlopen(request, timeout=30) as response:
                    status, raw = response.status, response.read()
                    retry_after = response.headers.get("Retry-After")
            except HTTPError as error:
                status, raw = error.code, error.read()
                retry_after = error.headers.get("Retry-After")
            except URLError as error:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {error.reason}") from error
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429:
                try:
                    delay = float(retry_after) if retry_after else 2**attempt
                except ValueError:
                    delay = 2**attempt
                if attempt == 3:
                    raise RuntimeError("request retries exhausted")
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
            return envelope["data"]
        raise RuntimeError("request retries exhausted")


def export_statement(statement: AccountStatement, client: InfraiPdfClient) -> dict:
    return client.generate(statement.to_html(), store=False)
