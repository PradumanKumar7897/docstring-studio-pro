"""
Tests for docgen.parser — Python source code parsing.

Covers:
  - Basic function / class extraction
  - Argument and return-type detection
  - Existing-docstring detection
  - Async functions
  - Edge-cases: empty code, invalid syntax, nested definitions
"""
import pytest
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════

def _make_parser(code: str):
    """Import parse_code and run it against *code*."""
    from docgen.parser import parse_code
    return parse_code(code)


# ══════════════════════════════════════════════════════
#  1. Basic Extraction
# ══════════════════════════════════════════════════════

class TestBasicExtraction:
    """Parser extracts the right number and types of items."""

    def test_single_function_found(self, simple_function_code):
        items = _make_parser(simple_function_code)
        assert len(items) >= 1

    def test_function_name_extracted(self, simple_function_code):
        items = _make_parser(simple_function_code)
        names = [i["name"] for i in items]
        assert "add" in names

    def test_function_type_label(self, simple_function_code):
        items = _make_parser(simple_function_code)
        func = next(i for i in items if i["name"] == "add")
        assert func["type"] == "function"

    def test_class_detected(self, simple_class_code):
        items = _make_parser(simple_class_code)
        types = [i["type"] for i in items]
        assert "class" in types

    def test_class_name_extracted(self, simple_class_code):
        items = _make_parser(simple_class_code)
        names = [i["name"] for i in items]
        assert "Calculator" in names

    def test_multiple_items_in_complex_code(self, complex_code):
        items = _make_parser(complex_code)
        assert len(items) >= 3

    def test_empty_code_returns_empty_list(self, empty_code):
        items = _make_parser(empty_code)
        assert items == []


# ══════════════════════════════════════════════════════
#  2. Argument Extraction
# ══════════════════════════════════════════════════════

class TestArgumentExtraction:
    """Parser captures parameter names and type annotations."""

    def test_args_list_present(self, simple_function_code):
        items = _make_parser(simple_function_code)
        func = next(i for i in items if i["name"] == "add")
        assert "args" in func

    def test_arg_names_correct(self, simple_function_code):
        items = _make_parser(simple_function_code)
        func = next(i for i in items if i["name"] == "add")
        arg_names = [a["name"] for a in func["args"]]
        assert "a" in arg_names
        assert "b" in arg_names

    def test_arg_type_annotations(self, simple_function_code):
        items = _make_parser(simple_function_code)
        func = next(i for i in items if i["name"] == "add")
        for arg in func["args"]:
            if arg["name"] in ("a", "b"):
                assert arg.get("type") == "int"

    def test_no_args_function(self, function_no_args_code):
        items = _make_parser(function_no_args_code)
        func = next(i for i in items if i["name"] == "get_version")
        assert func["args"] == []

    def test_self_excluded_from_method_args(self, simple_class_code):
        items = _make_parser(simple_class_code)
        methods = [i for i in items if i["name"] == "multiply"]
        if methods:
            arg_names = [a["name"] for a in methods[0]["args"]]
            assert "self" not in arg_names


# ══════════════════════════════════════════════════════
#  3. Return-Type Extraction
# ══════════════════════════════════════════════════════

class TestReturnTypeExtraction:
    """Parser captures return annotations."""

    def test_return_type_present(self, simple_function_code):
        items = _make_parser(simple_function_code)
        func = next(i for i in items if i["name"] == "add")
        assert "returns" in func

    def test_return_type_correct(self, simple_function_code):
        items = _make_parser(simple_function_code)
        func = next(i for i in items if i["name"] == "add")
        assert func["returns"] == "int"

    def test_no_return_annotation(self, empty_code):
        # A function with no annotation should return None or empty
        code = "def no_return():\n    pass"
        items = _make_parser(code)
        if items:
            assert items[0]["returns"] in (None, "", "None")


# ══════════════════════════════════════════════════════
#  4. Existing Docstring Detection
# ══════════════════════════════════════════════════════

class TestExistingDocstringDetection:
    """Parser correctly detects pre-existing docstrings."""

    def test_no_docstring_is_none_or_empty(self, simple_function_code):
        items = _make_parser(simple_function_code)
        func = next(i for i in items if i["name"] == "add")
        assert not func.get("docstring")

    def test_existing_docstring_detected(self, function_with_docstring_code):
        items = _make_parser(function_with_docstring_code)
        func = next(i for i in items if i["name"] == "greet")
        assert func.get("docstring") is not None


# ══════════════════════════════════════════════════════
#  5. Async Functions
# ══════════════════════════════════════════════════════

class TestAsyncFunctions:
    """Parser handles async def correctly."""

    def test_async_function_detected(self, async_function_code):
        items = _make_parser(async_function_code)
        names = [i["name"] for i in items]
        assert "fetch_data" in names

    def test_async_function_args(self, async_function_code):
        items = _make_parser(async_function_code)
        func = next(i for i in items if i["name"] == "fetch_data")
        arg_names = [a["name"] for a in func["args"]]
        assert "url" in arg_names


# ══════════════════════════════════════════════════════
#  6. Error / Edge Cases
# ══════════════════════════════════════════════════════

class TestEdgeCases:
    """Parser handles malformed / unusual input gracefully."""

    def test_invalid_python_raises_or_returns_empty(self, invalid_python_code):
        try:
            items = _make_parser(invalid_python_code)
            assert items == []
        except SyntaxError:
            pass  # also acceptable

    def test_returns_list_type(self, simple_function_code):
        items = _make_parser(simple_function_code)
        assert isinstance(items, list)

    def test_each_item_is_dict(self, complex_code):
        items = _make_parser(complex_code)
        for item in items:
            assert isinstance(item, dict)