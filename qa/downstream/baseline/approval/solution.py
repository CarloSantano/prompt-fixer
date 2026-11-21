"""Validate an approved message and prepare its payload without side effects.

Example::

    record = {
        "tenant_id": "tenant-1", "message_id": "message-1", "revision": 0,
        "recipient": " user@example.com ", "body": " Hello! ",
    }
    approval = {**record, "approved": True}
    payload = prepare_send(record, approval)
    assert payload["to"] == " user@example.com "
    assert payload["body"] == " Hello! "
    assert payload == prepare_send(record, approval)
"""

import json


def prepare_send(record: dict, approval: dict) -> dict:
    """Return a new payload, or raise ValueError for invalid input or approval.

    The key encodes all five values directly, so it has no digest collisions.
    Revisions use hexadecimal to support integers of arbitrary size without
    Python's configurable decimal conversion limit. Strings retain their exact
    content; whitespace is inspected only when validating blank values.
    """

    def validated_values(candidate, label):
        if not isinstance(candidate, dict):
            raise ValueError(f"{label} must be a dictionary")

        strings = []
        for field in ("tenant_id", "message_id", "recipient", "body"):
            value = candidate.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label}.{field} must be a nonblank string")
            strings.append(value)

        revision = candidate.get("revision")
        if (
            isinstance(revision, bool)
            or not isinstance(revision, int)
            or revision < 0
        ):
            raise ValueError(f"{label}.revision must be a nonnegative integer")

        return strings[0], strings[1], revision, strings[2], strings[3]

    values = validated_values(record, "record")
    if not isinstance(approval, dict):
        raise ValueError("approval must be a dictionary")
    if approval.get("approved") is not True:
        raise ValueError("approval.approved must be exactly True")

    if validated_values(approval, "approval") != values:
        raise ValueError("approval must match every required record field")

    tenant_id, message_id, revision, recipient, body = values
    encoded = json.dumps(
        [tenant_id, message_id, hex(revision), recipient, body],
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return {
        "to": recipient,
        "body": body,
        "idempotency_key": "prepare-send:v1:" + encoded,
    }
