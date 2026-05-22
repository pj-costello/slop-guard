#!/usr/bin/env python3
"""Unit tests for slop_lint (stdlib only, run with: python -m unittest)."""
import tempfile
import unittest
from pathlib import Path

# Import from repo root
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lint"))

import slop_lint  # noqa: E402


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class SyntaxValidationTest(unittest.TestCase):
    def test_flags_python_syntax_errors(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "broken.py", "def nope(:\n    pass\n")
            r = slop_lint.check_python_syntax(root)
            self.assertEqual(len(r), 1, r)
            self.assertEqual(r[0][0], "ERROR")
            self.assertIn("Syntax error", r[0][2])

    def test_allows_valid_python(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "ok.py", "def ok():\n    return 1\n")
            r = slop_lint.check_python_syntax(root)
            self.assertEqual(r, [])


class TrivialDocstringsTest(unittest.TestCase):
    def test_flags_short_obvious_docstring(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
def get_foo():
    """Get the foo."""
    return 1
''')
            r = slop_lint.check_trivial_docstrings(root)
            self.assertTrue(any("get_foo" in m for _, __, m in r))

    def test_allows_explanatory_docstring(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
def get_foo():
    """
    Resolves the foo with caching and retries on 429 from upstream.
    This is the single public entry for callers in other packages.
    """
    return 1
''')
            r = slop_lint.check_trivial_docstrings(root)
            self.assertEqual(r, [])


class CatchLogReraiseTest(unittest.TestCase):
    def test_two_line_log_reraise(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
import logging
log = logging.getLogger(__name__)
try:
    x = 1
except Exception as e:
    log.error("fail %s", e)
    raise
''')
            r = slop_lint.check_catch_log_reraise(root)
            self.assertEqual(len(r), 1, r)
            self.assertIn("re-raise", r[0][2])

    def test_multiline_log_then_reraise(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
import logging
log = logging.getLogger(__name__)
try:
    x = 1
except Exception as e:
    log.error("a")
    log.error("b")
    raise
''')
            r = slop_lint.check_catch_log_reraise(root)
            self.assertEqual(len(r), 1, r)

    def test_no_flag_when_except_does_not_only_log_before_raise(self):
        """Handler with assignment before raise is not "only log and re-raise"."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
import logging
log = logging.getLogger(__name__)
try:
    x = 1
except Exception as e:
    log.error("a")
    y = 1
    raise
''')
            r = slop_lint.check_catch_log_reraise(root)
            self.assertEqual(r, [])

    def test_flags_log_reraise_when_except_block_is_only_log_and_raise(self):
        """Try/finally is separate; except body [log, raise] still matches."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
import logging
log = logging.getLogger(__name__)
try:
    x = 1
except Exception as e:
    log.error("a")
    raise
finally:
    pass
''')
            r = slop_lint.check_catch_log_reraise(root)
            self.assertEqual(len(r), 1)

    def test_allows_bare_except_reraise_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
try:
    x = 1
except Exception:
    raise
''')
            r = slop_lint.check_catch_log_reraise(root)
            self.assertEqual(r, [])

    def test_allows_exception_translation_after_log(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", '''
import logging
log = logging.getLogger(__name__)
try:
    value = config["missing"]
except KeyError as e:
    log.error("missing key")
    raise ValueError("Invalid config") from e
''')
            r = slop_lint.check_catch_log_reraise(root)
            self.assertEqual(r, [])


class TestFilesOutsideTestsTest(unittest.TestCase):
    def test_finds_misplaced_test(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "app/test_foo.py", "x = 1\n")
            r = slop_lint.check_test_files_outside_tests(root)
            self.assertTrue(any("test_foo" in f for _, f, _ in r))
            self.assertTrue(any(s == "ERROR" for s, _, _ in r))

    def test_ignores_tests_dir(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "tests/test_foo.py", "x = 1\n")
            r = slop_lint.check_test_files_outside_tests(root)
            self.assertEqual(r, [])


    def test_deduplicates_files_matching_multiple_test_patterns(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "app/test_foo.test.py", "x = 1\n")
            r = slop_lint.check_test_files_outside_tests(root)
            self.assertEqual(len(r), 1, r)

    def test_finds_misplaced_javascript_spec(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "src/widget.spec.ts", "export const x = 1\n")
            r = slop_lint.check_test_files_outside_tests(root)
            self.assertEqual(len(r), 1, r)
            self.assertEqual(r[0][0], "ERROR")


class EmptyFilesTest(unittest.TestCase):
    def test_truly_empty_py(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "empty.py").write_text("", encoding="utf-8")
            r = slop_lint.check_empty_files(root)
            self.assertTrue(
                any("no meaningful" in m.lower() for _, __, m in r),
                r,
            )

    def test_allows_init_with_only_imports(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "__init__.py").write_text("from . import x\n", encoding="utf-8")
            r = slop_lint.check_empty_files(root)
            self.assertEqual(
                r,
                [],
            )

    def test_docstring_only_py_has_no_meaningful_code(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "placeholder.py", '"""Placeholder module."""\n')
            r = slop_lint.check_empty_files(root)
            self.assertEqual(len(r), 1, r)

    def test_pass_only_py_has_no_meaningful_code(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "placeholder.py", "pass\n")
            r = slop_lint.check_empty_files(root)
            self.assertEqual(len(r), 1, r)

    def test_import_only_non_init_has_no_meaningful_code(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "placeholder.py", "import os\nfrom pathlib import Path\n")
            r = slop_lint.check_empty_files(root)
            self.assertEqual(len(r), 1, r)

    def test_allows_file_with_function(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "useful.py", "def useful():\n    return 1\n")
            r = slop_lint.check_empty_files(root)
            self.assertEqual(r, [])


class SourceStringSlicingTest(unittest.TestCase):
    def test_flags_triple_quote_split(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", """
src = "x"
html = src.split('\"\"\"')[1]
""")
            r = slop_lint.check_source_string_slicing(root)
            self.assertEqual(len(r), 1, r)

    def test_allows_normal_split(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", 'parts = "a,b".split(",")\n')
            r = slop_lint.check_source_string_slicing(root)
            self.assertEqual(r, [])


class GenericErrorMessagesTest(unittest.TestCase):
    def test_flags_generic_raise_message(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", 'raise ValueError("Invalid input")\n')
            r = slop_lint.check_generic_error_messages(root)
            self.assertEqual(len(r), 1, r)
            self.assertIn("generic error", r[0][2])

    def test_allows_contextual_raise_message(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", 'raise ValueError(f"Could not parse document {doc_id}: expected JSON")\n')
            r = slop_lint.check_generic_error_messages(root)
            self.assertEqual(r, [])


class SpeculativeLoggingTest(unittest.TestCase):
    def test_flags_routine_info_log(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", """
import logging
log = logging.getLogger(__name__)
log.info("Entering evaluate_review")
""")
            r = slop_lint.check_speculative_logging(root)
            self.assertEqual(len(r), 1, r)

    def test_allows_state_transition_error_log(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", """
import logging
log = logging.getLogger(__name__)
log.error("review_store_failed", extra={"doc_id": doc_id})
""")
            r = slop_lint.check_speculative_logging(root)
            self.assertEqual(r, [])


class SilentCatchesTest(unittest.TestCase):
    def test_flags_bare_silent_catch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", """
try:
    risky()
except Exception:
    pass
""")
            r = slop_lint.check_silent_catches(root)
            self.assertEqual(len(r), 1, r)
            self.assertEqual(r[0][0], "ERROR")

    def test_allows_intentional_silent_catch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", """
try:
    optional_cleanup()
except FileNotFoundError:  # INTENTIONAL: cleanup target may already be gone
    pass
""")
            r = slop_lint.check_silent_catches(root)
            self.assertEqual(r, [])

    def test_allows_non_silent_handler(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.py", """
try:
    risky()
except Exception as e:
    raise RuntimeError("Could not run risky operation") from e
""")
            r = slop_lint.check_silent_catches(root)
            self.assertEqual(r, [])


if __name__ == "__main__":
    unittest.main()
