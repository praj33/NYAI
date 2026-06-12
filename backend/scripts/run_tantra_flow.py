#!/usr/bin/env python3
"""CLI entry point for local TANTRA flow verification."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tantra.flow import run_tantra_flow


def main() -> int:
    query = sys.argv[1] if len(sys.argv) > 1 else "theft of mobile phone"
    print("=== TANTRA END-TO-END FLOW ===\n")
    result = run_tantra_flow(query)
    print(json.dumps(result, indent=2, default=str))
    print(f"\n=== FLOW STATUS: {result['flow_status']} ===")
    return 0 if result.get("flow_status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
