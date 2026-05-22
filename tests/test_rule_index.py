#!/usr/bin/env python3
"""Tests for rule/source/index synchronization."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validate_rule_index  # noqa: E402


class RuleIndexValidationTest(unittest.TestCase):
    def test_current_rule_index_is_valid(self):
        self.assertEqual(validate_rule_index.validate(), [])

    def test_rule_headings_are_loaded_with_categories(self):
        headings = validate_rule_index.load_rule_headings()
        self.assertTrue(any(
            h["category"] == "Context & Proof" and h["title"] == "Match the proof to the claim"
            for h in headings
        ))


if __name__ == "__main__":
    unittest.main()
