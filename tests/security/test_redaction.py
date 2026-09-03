from hireme_ai.profile.redactor import redact_pii


def test_redacts_email_phone() -> None:
    text = redact_pii("me@example.com +91 98765 43210")
    assert "example.com" not in text
    assert "98765" not in text
