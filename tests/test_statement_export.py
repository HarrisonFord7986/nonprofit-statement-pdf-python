from src.statement_export import AccountStatement, Donation


def test_statement_total_and_privacy_safe_html():
    statement = AccountStatement(
        "Ava Singh", "DONOR-7", (Donation("2026-04-01", 25.5, "Food pantry"),)
    )
    html = statement.to_html()
    assert statement.total == 25.5
    assert "Food pantry" in html
    assert "$25.50" in html
    assert "Ava Singh" in html
    assert "email" not in html.lower()

