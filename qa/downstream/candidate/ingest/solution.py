"""Ingest an event without mutating or aliasing either input.

Example:
    >>> event = {"tenant_id": "acme", "message_id": "m1", "subject": ["hello"]}
    >>> saved, result = ingest(event, {})
    >>> result["created"], result["record"]["status"]
    (True, 'needs_review')
    >>> result["record"]["subject"].append("detached")
    >>> event["subject"]
    ['hello']
    >>> again, duplicate = ingest(dict(event, subject="ignored"), saved)
    >>> duplicate["created"], duplicate["record"] == saved[("acme", "m1")]
    (False, True)
"""


def ingest(event, store):
    """Return a detached updated store and a creation/duplicate result.

    IDs retain their supplied spelling and whitespace. Returned records may
    share data with each other, but never with either input.
    """
    from copy import deepcopy

    tenant_id = event.get("tenant_id")
    message_id = event.get("message_id")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id must be a non-whitespace string")
    if not isinstance(message_id, str) or not message_id.strip():
        raise ValueError("message_id must be a non-whitespace string")

    key = (tenant_id, message_id)
    created = key not in store
    new_store = deepcopy(store)

    if created:
        # Copy the IDs too: string subclasses can carry mutable attributes.
        key, subject = deepcopy((key, event.get("subject", "")))
        new_store[key] = {
            "tenant_id": key[0],
            "message_id": key[1],
            "subject": subject,
            "status": "needs_review",
        }

    return new_store, {"created": created, "record": new_store[key]}
