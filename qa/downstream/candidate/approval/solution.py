"""Prepare an explicitly approved message without sending it.

Usage example:
    >>> record = {"tenant_id": "tenant-a", "message_id": "msg-7",
    ...           "revision": 0, "recipient": "person@example.com",
    ...           "body": " Hello "}
    >>> approval = dict(record, approved=True)
    >>> payload = prepare_send(record, approval)
    >>> payload["to"], payload["body"]
    ('person@example.com', ' Hello ')
    >>> payload == prepare_send(record, approval)
    True
"""


def prepare_send(record: dict, approval: dict) -> dict:
    """Validate approval and return a fresh payload of immutable scalar values.

    Required strings retain their original whitespace and Unicode content.
    Invalid inputs, denied approval, and mismatches raise ValueError.
    """
    import base64

    if not isinstance(record, dict) or not isinstance(approval, dict):
        raise ValueError("record and approval must be dictionaries")

    string_fields = ("tenant_id", "message_id", "recipient", "body")

    def validated_values(source, label):
        values = {}
        for field in string_fields:
            value = source.get(field)
            if not isinstance(value, str):
                raise ValueError(f"{label}.{field} must be a nonblank string")
            # Extract a built-in immutable str even when given a str subclass.
            value = str.__str__(value)
            if not value.strip():
                raise ValueError(f"{label}.{field} must be a nonblank string")
            values[field] = value

        revision = source.get("revision")
        if not isinstance(revision, int) or isinstance(revision, bool):
            raise ValueError(f"{label}.revision must be a nonnegative integer")
        revision = int.__int__(revision)
        if revision < 0:
            raise ValueError(f"{label}.revision must be a nonnegative integer")
        values["revision"] = revision
        return values

    record_values = validated_values(record, "record")
    if approval.get("approved") is not True:
        raise ValueError("approval.approved must be exactly True")
    approval_values = validated_values(approval, "approval")

    for field in (*string_fields, "revision"):
        if record_values[field] != approval_values[field]:
            raise ValueError(f"approval.{field} does not match record.{field}")

    # Length-prefixed UTF-8 fields make the encoding unambiguous. Surrogatepass
    # also distinguishes every Python string, including lone surrogate values.
    # Reversible encoding (rather than a fixed-size hash) ensures that changing
    # any field changes the key, without relying on a no-collision assumption.
    key_fields = (
        record_values["tenant_id"],
        record_values["message_id"],
        # Hexadecimal supports arbitrarily large ints without the interpreter's
        # configurable decimal conversion limit.
        format(record_values["revision"], "x"),
        record_values["recipient"],
        record_values["body"],
    )
    parts = []
    for value in key_fields:
        encoded = value.encode("utf-8", errors="surrogatepass")
        parts.append(str(len(encoded)).encode("ascii") + b":" + encoded)
    key = "send-v1:" + base64.urlsafe_b64encode(b"".join(parts)).decode("ascii")

    return {
        "to": record_values["recipient"],
        "body": record_values["body"],
        "idempotency_key": key,
    }
