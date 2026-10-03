import json

from src.statement_export import AccountStatement, Donation, InfraiPdfClient, export_statement


statement = AccountStatement(
    donor_name="Mina Chen",
    account_id="DONOR-1042",
    donations=(
        Donation("2026-01-15", 75.0, "Community Health Kits"),
        Donation("2026-03-02", 120.0, "Clinic Transport"),
    ),
)
result = export_statement(statement, InfraiPdfClient())
print(json.dumps(result, indent=2, sort_keys=True))

