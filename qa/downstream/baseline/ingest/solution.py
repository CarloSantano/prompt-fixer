"""Create tenant-scoped records without mutating or retaining mutable inputs.

Usage:
    store, result = ingest({"tenant_id": "acme", "message_id": "m1"}, {})
    assert result["created"] is True
    assert store[("acme", "m1")]["subject"] == ""

Run this file to execute deterministic local assertions.
"""

from copy import deepcopy


def ingest(event, store):
    """Return ``(new_store, result)`` with mutable data isolated from inputs.

    Valid identifiers are preserved verbatim. Duplicate events retain the full
    stored record, including additional fields, and ignore incoming replacements.
    The returned store and result may share their copied record with each other.
    """
    tenant_id = event.get("tenant_id")
    message_id = event.get("message_id")
    for name, value in (("tenant_id", tenant_id), ("message_id", message_id)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-whitespace string")

    key = (tenant_id, message_id)
    new_store = deepcopy(store)
    created = key not in new_store
    if created:
        new_store[key] = {
            "tenant_id": tenant_id,
            "message_id": message_id,
            "subject": deepcopy(event.get("subject", "")),
            "status": "needs_review",
        }

    return new_store, {"created": created, "record": new_store[key]}


def _check():
    unrelated_key = ("other", "old")
    original_store = {
        unrelated_key: {"subject": {"tags": ["original"]}, "extra": [1]}
    }
    event = {
        "tenant_id": " tenant ",
        "message_id": " message ",
        "subject": {"text": ["hello"]},
        "ignored": {"values": [99]},
    }
    store_before, event_before = deepcopy(original_store), deepcopy(event)
    new_store, result = ingest(event, original_store)
    key = (" tenant ", " message ")
    assert result == {
        "created": True,
        "record": {
            "tenant_id": " tenant ",
            "message_id": " message ",
            "subject": {"text": ["hello"]},
            "status": "needs_review",
        },
    }
    assert new_store[key] == result["record"]
    assert new_store[unrelated_key] == original_store[unrelated_key]
    assert original_store == store_before and event == event_before

    # Both outputs can be mutated without touching either input.
    result["record"]["subject"]["text"].append("result mutation")
    new_store[key]["subject"]["text"].append("store mutation")
    new_store[unrelated_key]["subject"]["tags"].append("unrelated mutation")
    new_store[unrelated_key]["extra"].append(2)
    assert original_store == store_before and event == event_before

    duplicate_key = ("acme", "same")
    stored_record = {
        "tenant_id": "acme",
        "message_id": "same",
        "subject": {"text": ["stored subject"]},
        "status": "done",
        "additional": {"history": ["kept"]},
    }
    duplicate_store = {duplicate_key: stored_record, **original_store}
    duplicate_event = {
        "tenant_id": "acme",
        "message_id": "same",
        "subject": {"text": ["replacement subject"]},
        "status": "replacement status",
    }
    duplicate_before = deepcopy(duplicate_store)
    duplicate_event_before = deepcopy(duplicate_event)
    copied_store, duplicate = ingest(duplicate_event, duplicate_store)
    assert duplicate == {"created": False, "record": stored_record}
    assert copied_store == duplicate_before
    assert duplicate["record"] is not stored_record
    assert copied_store[duplicate_key] is not stored_record
    duplicate["record"]["subject"]["text"].append("result mutation")
    copied_store[duplicate_key]["additional"]["history"].append("store mutation")
    copied_store[unrelated_key]["extra"].append(3)
    assert duplicate_store == duplicate_before
    assert duplicate_event == duplicate_event_before

    # Identical message IDs are independent across tenants.
    tenant_store, tenant_result = ingest(
        {"tenant_id": "second", "message_id": "same"}, duplicate_store
    )
    assert tenant_result["created"] is True
    assert tenant_store[duplicate_key] == stored_record
    assert tenant_store[("second", "same")]["subject"] == ""
    assert len(tenant_store) == len(duplicate_store) + 1

    # Only an absent subject defaults to the empty string.
    for subject in (None, False, 0, [], {}):
        supplied = {"tenant_id": "t", "message_id": "m", "subject": subject}
        _, supplied_result = ingest(supplied, {})
        assert supplied_result["record"]["subject"] == subject
        assert type(supplied_result["record"]["subject"]) is type(subject)

    # Missing and invalid identifiers fail without changing either input.
    for field in ("tenant_id", "message_id"):
        for invalid in (None, False, 123, [], {}, "", " \t\n"):
            invalid_event = {"tenant_id": "t", "message_id": "m", field: invalid}
            before = deepcopy(invalid_event)
            try:
                ingest(invalid_event, duplicate_store)
            except ValueError:
                pass
            else:
                raise AssertionError(f"Accepted invalid {field}: {invalid!r}")
            assert invalid_event == before and duplicate_store == duplicate_before
        missing_event = {"tenant_id": "t", "message_id": "m"}
        del missing_event[field]
        before = deepcopy(missing_event)
        try:
            ingest(missing_event, duplicate_store)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Accepted missing {field}")
        assert missing_event == before and duplicate_store == duplicate_before


if __name__ == "__main__":
    _check()
    print("All local assertions passed.")
