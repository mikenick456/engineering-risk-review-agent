import sys

from tools import review_application


def format_review(result):
    lines = [
        f"Summary: {result['apply_no']} risk level is {result['risk_level']}.",
        f"Risk level: {result['risk_level']}",
        f"Blocked: {str(result['blocked']).lower()}",
        "Findings:",
    ]

    if result["findings"]:
        lines.extend(f"- {finding}" for finding in result["findings"])
    else:
        lines.append("- none")

    lines.append("Evidence:")
    lines.extend(f"- {item}" for item in result["evidence"])
    lines.extend([
        f"Recommended next action: {result['recommended_next_action']}",
        f"Safety note: {result['safety_note']}",
    ])
    return "\n".join(lines)


def main(argv):
    if len(argv) != 2:
        print("Usage: py app/agent.py <ApplyNo>")
        return 2

    result = review_application(argv[1])
    print(format_review(result))
    return 0 if not result["blocked"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
