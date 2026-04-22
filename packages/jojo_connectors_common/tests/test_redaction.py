from jojo_connectors_common.redaction import redact_pii


def test_redacts_ssn():
    r = redact_pii("SSN: 123-45-6789 on file")
    assert "123-45-6789" not in r.content
    assert "[REDACTED:ssn]" in r.content
    assert "ssn" in r.redacted_fields


def test_redacts_email_but_preserves_noreply():
    r = redact_pii("Contact alice@nurixtx.com or noreply@nurixtx.com for info.")
    assert "alice@nurixtx.com" not in r.content
    assert "noreply@nurixtx.com" in r.content  # whitelisted
    assert "email" in r.redacted_fields


def test_redacts_us_phone_variants():
    samples = [
        "(415) 555-2671",
        "415-555-2671",
        "415.555.2671",
        "+1 415 555 2671",
    ]
    for s in samples:
        r = redact_pii(f"Call me at {s}.")
        assert s not in r.content, f"{s} was not redacted"
        assert "[REDACTED:phone]" in r.content


def test_redacts_patient_id_prefixes():
    r = redact_pii("Record for PT:1234567 and MRN-9876543 attached.")
    assert "PT:1234567" not in r.content
    assert "MRN-9876543" not in r.content
    assert "patient_id" in r.redacted_fields


def test_redacts_dob():
    r = redact_pii("DOB: 01/23/1980 per record; ref 1980-01-23.")
    assert "01/23/1980" not in r.content
    assert "1980-01-23" not in r.content
    assert "dob" in r.redacted_fields


def test_no_redaction_returns_empty_list():
    r = redact_pii("Hello world.")
    assert r.redacted_fields == []
    assert r.content == "Hello world."


def test_match_counts_aggregate():
    r = redact_pii("alice@x.com and bob@x.com and carol@x.com")
    assert r.match_counts["email"] == 3
