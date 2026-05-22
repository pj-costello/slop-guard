#!/usr/bin/env python3
"""
slop_lint.py -- Portable lint checks for AI-generated code anti-patterns.

Usage:
    python slop_lint.py [root_dir]       # defaults to current directory

Import individual checks:
    from slop_lint import check_trivial_docstrings
    results = check_trivial_docstrings("/path/to/project")

Each check returns a list of (severity, filepath, message) tuples.
Exit code: 0 = all passed, 1 = one or more errors (warnings don't fail).
"""
import ast
import re
import sys
from pathlib import Path

EXCLUDE_DIRS = {".venv", "__pycache__", ".git", ".claude", "node_modules", ".tox", "venv"}


def _py_files(root):
    root = Path(root)
    for path in root.glob("**/*.py"):
        if not any(p in EXCLUDE_DIRS for p in path.parts):
            yield path


def _normalize_name(name):
    """Split function name into lowercase word set: get_db_client -> {get, db, client}."""
    words = set()
    for part in name.split("_"):
        if part:
            words.add(part.lower())
    return words


def _normalize_docstring(doc):
    """Extract lowercase words from first line of docstring."""
    first_line = doc.strip().split("\n")[0]
    first_line = re.sub(r"[^a-zA-Z\s]", "", first_line)
    return set(first_line.lower().split())


def _read_python_source(path):
    return path.read_text(encoding="utf-8")


def _parse_python_file(path):
    return ast.parse(_read_python_source(path), filename=str(path))


def _count_body_lines(node):
    """Count non-empty lines in a function body (excluding docstring)."""
    if not node.body:
        return 0
    start = node.body[0]
    if isinstance(start, ast.Expr) and isinstance(start.value, ast.Constant):
        body = node.body[1:]
    else:
        body = node.body
    if not body:
        return 0
    return body[-1].end_lineno - body[0].lineno + 1


def check_python_syntax(root_dir):
    """Error on Python files that cannot be parsed as UTF-8 Python source."""
    results = []
    root = Path(root_dir)

    for path in _py_files(root):
        try:
            _parse_python_file(path)
        except SyntaxError as e:
            rel = path.relative_to(root)
            location = f"line {e.lineno}" if e.lineno else "unknown line"
            results.append((
                "ERROR",
                str(rel),
                f"Syntax error at {location}: {e.msg}"
            ))
        except UnicodeDecodeError as e:
            rel = path.relative_to(root)
            results.append((
                "ERROR",
                str(rel),
                f"Could not decode Python file as UTF-8: {e.reason}"
            ))

    return results


def check_trivial_docstrings(root_dir, exclude_files=None):
    """Warn on functions with docstrings that just restate the function name.

    Flags functions where:
    - Docstring first line is < 8 words
    - Function body is < 5 lines
    - Docstring words are largely a restatement of the function name
    """
    results = []
    exclude_files = set(exclude_files or [])
    filler_words = {"the", "a", "an", "and", "or", "of", "to", "for", "in", "is",
                    "return", "returns", "get", "set", "this", "that", "from"}

    for path in _py_files(root_dir):
        if path.name in exclude_files:
            continue
        try:
            tree = _parse_python_file(path)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.body:
                continue

            first = node.body[0]
            if not isinstance(first, ast.Expr):
                continue
            if not isinstance(first.value, ast.Constant):
                continue
            if not isinstance(first.value.value, str):
                continue

            doc = first.value.value
            doc_words = _normalize_docstring(doc)
            if len(doc_words) >= 8:
                continue

            body_lines = _count_body_lines(node)
            if body_lines >= 5:
                continue

            name_words = _normalize_name(node.name)
            doc_content = doc_words - filler_words
            name_content = name_words - filler_words

            if doc_content and doc_content.issubset(name_content | filler_words):
                rel = path.relative_to(root_dir)
                results.append((
                    "WARN",
                    str(rel),
                    f"Line {node.lineno}: `{node.name}` has a trivial docstring "
                    f"that restates the function name. Consider removing it."
                ))

    return results


_LOG_ATTRS = {"error", "warning", "warn", "info", "debug", "critical", "exception"}


def _is_logger_call_expr(stmt):
    if not isinstance(stmt, ast.Expr):
        return False
    if not isinstance(stmt.value, ast.Call):
        return False
    call = stmt.value
    if isinstance(call.func, ast.Attribute) and call.func.attr in _LOG_ATTRS:
        return True
    return False


def _is_discardable_string_expr(stmt):
    """Allow a lone string literal in an except block (e.g. accidental 'docstring')."""
    if not isinstance(stmt, ast.Expr):
        return False
    v = stmt.value
    if isinstance(v, ast.Constant) and isinstance(v.value, str):
        return True
    return False


def _is_log_and_reraise_handler(body):
    """True if body is: [optional str exprs and logger calls...] + bare raise."""
    if not body or not isinstance(body[-1], ast.Raise):
        return False
    if body[-1].exc is not None:
        return False
    for stmt in body[:-1]:
        if _is_logger_call_expr(stmt) or _is_discardable_string_expr(stmt):
            continue
        return False
    if len(body) < 2:
        return False
    for stmt in body[:-1]:
        if _is_logger_call_expr(stmt):
            return True
    return False


def check_catch_log_reraise(root_dir, exclude_files=None):
    """Warn on try/except blocks that only log and re-raise.

    Pattern: except ...: (optional noise) logger.error(...); [more logs] raise
    This adds no value -- let the exception propagate.
    """
    results = []
    exclude_files = set(exclude_files or ["error_handler.py", "exceptions.py"])

    for path in _py_files(root_dir):
        if path.name in exclude_files:
            continue
        try:
            tree = _parse_python_file(path)
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue

            for handler in node.handlers:
                if not _is_log_and_reraise_handler(handler.body):
                    continue
                rel = path.relative_to(root_dir)
                results.append((
                    "WARN",
                    str(rel),
                    f"Line {handler.lineno}: try/except that only logs and "
                    f"re-raises adds no value. Let the exception propagate."
                ))

    return results


def check_test_files_outside_tests(root_dir):
    """Error on test files found outside test directories.

    AI tools sometimes generate test files alongside source code.
    These must never ship in production paths.
    """
    results = []
    seen = set()
    test_patterns = ["*.test.py", "*_test.py", "test_*.py", "*.test.js",
                     "*.test.ts", "*.test.jsx", "*.test.tsx", "*.spec.js",
                     "*.spec.ts", "*.spec.jsx", "*.spec.tsx"]
    test_dirs = {"tests", "test", "__tests__", "spec", "specs"}
    root = Path(root_dir)

    for pattern in test_patterns:
        for path in root.glob(f"**/{pattern}"):
            if any(p in EXCLUDE_DIRS for p in path.parts):
                continue
            rel = path.relative_to(root)
            if any(p in test_dirs for p in rel.parts):
                continue
            if rel in seen:
                continue
            seen.add(rel)
            results.append((
                "ERROR",
                str(rel),
                f"Test file found outside tests/ directory. "
                f"Move to tests/ or delete if unused."
            ))

    return results


def _is_meaningless_module_stmt(stmt):
    if isinstance(stmt, (ast.Import, ast.ImportFrom, ast.Pass)):
        return True
    if isinstance(stmt, ast.Expr):
        value = stmt.value
        if isinstance(value, ast.Constant) and isinstance(value.value, (str, type(Ellipsis))):
            return True
    return False


def check_empty_files(root_dir, exclude_files=None):
    """Warn on Python files with no meaningful content."""
    results = []
    exclude_files = set(exclude_files or ["__init__.py"])
    root = Path(root_dir)

    for path in _py_files(root):
        if path.name in exclude_files:
            continue
        try:
            tree = _parse_python_file(path)
        except (SyntaxError, UnicodeDecodeError):
            continue

        meaningful = [stmt for stmt in tree.body if not _is_meaningless_module_stmt(stmt)]
        if not meaningful:
            rel = path.relative_to(root)
            results.append((
                "WARN",
                str(rel),
                f"File has no meaningful code. Delete if unused."
            ))

    return results


def main(root_dir=None):
    root = Path(root_dir or ".").resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(2)

    all_results = []
    all_results.extend(check_python_syntax(root))
    all_results.extend(check_trivial_docstrings(root))
    all_results.extend(check_catch_log_reraise(root))
    all_results.extend(check_test_files_outside_tests(root))
    all_results.extend(check_empty_files(root))

    errors = [r for r in all_results if r[0] == "ERROR"]
    warnings = [r for r in all_results if r[0] == "WARN"]

    if warnings:
        print(f"\n  Slop Guard: {len(warnings)} warning(s)")
        for severity, filepath, msg in warnings:
            print(f"  WARN  [{filepath}]: {msg}")

    if errors:
        print(f"\n  Slop Guard: {len(errors)} error(s)")
        for severity, filepath, msg in errors:
            print(f"  ERROR [{filepath}]: {msg}")

    if not errors and not warnings:
        print("  Slop Guard: all checks passed")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
