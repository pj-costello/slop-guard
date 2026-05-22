#!/usr/bin/env python3
"""Validate that RULES.md, SOURCES.md, and rules.json stay synchronized."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "RULES.md"
SOURCES = ROOT / "SOURCES.md"
INDEX = ROOT / "rules.json"

REQUIRED_FIELDS = {"id", "title", "category", "source", "enforcement", "lint_checks"}
VALID_ENFORCEMENT = {"automated_error", "automated_warn", "manual_review", "review_packet"}


def load_rule_headings(path=RULES):
    headings = []
    current_category = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_category = line[3:].strip()
        elif line.startswith("### "):
            headings.append({"category": current_category, "title": line[4:].strip()})
    return headings


def load_index(path=INDEX):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("rules.json schema_version must be 1")
    rules = data.get("rules")
    if not isinstance(rules, list):
        raise ValueError("rules.json must contain a rules list")
    return rules


def validate(root=ROOT):
    errors = []
    rule_headings = load_rule_headings(root / "RULES.md")
    indexed_rules = load_index(root / "rules.json")
    sources_text = (root / "SOURCES.md").read_text(encoding="utf-8")

    heading_pairs = [(r["category"], r["title"]) for r in rule_headings]
    index_pairs = [(r.get("category"), r.get("title")) for r in indexed_rules]

    if len(index_pairs) != len(set(index_pairs)):
        errors.append("rules.json contains duplicate category/title entries")
    ids = [r.get("id") for r in indexed_rules]
    if len(ids) != len(set(ids)):
        errors.append("rules.json contains duplicate ids")

    missing_from_index = sorted(set(heading_pairs) - set(index_pairs))
    extra_in_index = sorted(set(index_pairs) - set(heading_pairs))
    if missing_from_index:
        errors.append("RULES.md headings missing from rules.json: " + repr(missing_from_index))
    if extra_in_index:
        errors.append("rules.json entries missing from RULES.md: " + repr(extra_in_index))

    for rule in indexed_rules:
        missing_fields = REQUIRED_FIELDS - set(rule)
        if missing_fields:
            errors.append(f"{rule.get('title', '<unknown>')} missing fields: {sorted(missing_fields)}")
        if rule.get("enforcement") not in VALID_ENFORCEMENT:
            errors.append(f"{rule.get('title', '<unknown>')} has invalid enforcement: {rule.get('enforcement')}")
        if not isinstance(rule.get("lint_checks"), list):
            errors.append(f"{rule.get('title', '<unknown>')} lint_checks must be a list")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(rule.get("id", ""))):
            errors.append(f"{rule.get('title', '<unknown>')} has non-kebab-case id: {rule.get('id')}")

    for _, title in heading_pairs:
        if title not in sources_text:
            errors.append(f"RULES.md heading not referenced in SOURCES.md: {title}")

    return errors


def main():
    errors = validate()
    if errors:
        print("Rule index validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("Rule index validation passed")


if __name__ == "__main__":
    main()
