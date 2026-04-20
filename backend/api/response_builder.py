"""
Response Builder — TANTRA Formatter Gate
Enforces that every response passes through a structured validation gate.
Stamps metadata.formatted = true as proof of compliance.
No response may bypass this gate.
"""
from datetime import datetime
from typing import Dict, Any, List

FORMATTER_VERSION = "1.0.0"

REQUIRED_FIELDS = [
    "domain",
    "jurisdiction",
    "enforcement_decision",
    "trace_id",
    "confidence",
    "legal_route",
]


class ResponseNotFormatted(Exception):
    """Raised when a response is missing required fields and cannot be formatted."""
    pass


class ResponseBuilder:
    """
    Formatter gate that validates and stamps every response before it leaves the pipeline.
    TANTRA requirement: no response may be returned without metadata.formatted = true.
    """

    def build(self, raw_response: dict) -> dict:
        """
        Validate response completeness and stamp metadata.
        Raises ResponseNotFormatted if required fields are missing.
        """
        missing = [f for f in REQUIRED_FIELDS if f not in raw_response or raw_response[f] is None]
        if missing:
            raise ResponseNotFormatted(
                f"Response failed formatter gate — missing fields: {missing}. "
                f"trace_id={raw_response.get('trace_id', 'UNKNOWN')}"
            )

        # Stamp metadata as proof the response passed the formatter gate
        raw_response["metadata"] = {
            "formatted": True,
            "formatter_version": FORMATTER_VERSION,
            "formatted_at": datetime.utcnow().isoformat(),
            "schema_compliant": True,
            "required_fields_validated": len(REQUIRED_FIELDS),
        }

        return raw_response