#!/usr/bin/env python3
"""Check ``juju status --format=json`` output for errors and unsettled units.

Reads JSON from stdin and exits:

  0  if every unit agent is idle and no application/unit reports an error
  1  if any application or unit reports an error status
  2  if any unit agent is not yet idle (still waiting/executing/allocating)

Exit code 2 lets the caller keep polling until the deployment settles.
"""

import json
import sys


def check(data):
    errors = []
    pending = []

    for name, app in (data.get("applications") or {}).items():
        app_status = (app.get("status") or {}).get("status", "")
        if app_status == "error":
            errors.append(f"application {name!r} is in error state")

        for unit_name, unit in (app.get("units") or {}).items():
            agent_status = (unit.get("agent-status") or {}).get("status", "")
            ws = (unit.get("workload-status") or {}).get("status", "")
            if agent_status == "error":
                errors.append(f"unit {unit_name!r} agent is in error state")
            if ws == "error":
                errors.append(f"unit {unit_name!r} is in error state")
            if agent_status != "idle":
                pending.append(
                    f"unit {unit_name!r} agent status is {agent_status!r}"
                )

    return errors, pending


def main():
    data = json.load(sys.stdin)
    errors, pending = check(data)

    if errors:
        print("\n".join(errors))
        return 1
    if pending:
        print("\n".join(pending))
        return 2

    print("All units settled with no error states.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
