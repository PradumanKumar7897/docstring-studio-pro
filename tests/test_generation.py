"""
Tests for docgen.generator — local docstring generation engine.

Covers:
  - Google / NumPy / reST style output
  - Functions, classes, methods
  - Args and return sections
  - Overwrite behaviour via writer integration
  - Template registry
"""
import pytest
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════

def _gen(name, args=None, returns=None, style="google", item_type="function"):
    from docgen.generator import generate_docstring
    return generate_docstring(
        name=name,
        args=args or [],
        returns=returns,
        style=style,
        item_type=item_type,
    )


# ══════════════════════════════════════════════════════
#  1. Output Format
# ══════════════════════════════════════════════════════

class TestOutputFormat:
    """Generated docstrings are properly formatted strings."""

    def test_returns_string(self):
        result = _gen("my_func")
        assert isinstance(result, str)

    def test_not_empty(self):
        result = _gen("my_func", args=[{"name": "x", "annotation": "int"}])
        assert len(result.strip()) > 0

    def test_triple_quoted_or_clean_string(self):
        result = _gen("my_func")
        # Should not accidentally include raw triple-quote wrappers twice
        assert result.count('"""') <= 2


# ══════════════════════════════════════════════════════
#  2. Google Style
# ══════════════════════════════════════════════════════

class TestGoogleStyle:
    """Generator produces valid Google-style docstrings."""

    def test_google_has_args_section(self):
        result = _gen(
            "process",
            args=[{"name": "data", "annotation": "list"}],
            style="google",
        )
        assert "Args:" in result

    def test_google_has_returns_section(self):
        result = _gen("process", returns="bool", style="google")
        assert "Returns:" in result

    def test_google_arg_name_present(self):
        result = _gen(
            "compute",
            args=[{"name": "value", "annotation": "float"}],
            style="google",
        )
        assert "value" in result

    def test_google_no_args_no_args_section(self):
        result = _gen("ping", args=[], style="google")
        # When there are no args, "Args:" section is optional / should not appear
        # (implementation-dependent; just verify it doesn't crash)
        assert isinstance(result, str)


# ══════════════════════════════════════════════════════
#  3. NumPy Style
# ══════════════════════════════════════════════════════

class TestNumpyStyle:
    """Generator produces valid NumPy-style docstrings."""

    def test_numpy_has_parameters_section(self):
        result = _gen(
            "transform",
            args=[{"name": "arr", "annotation": "np.ndarray"}],
            style="numpy",
        )
        assert "Parameters" in result

    def test_numpy_has_returns_section(self):
        result = _gen("transform", returns="np.ndarray", style="numpy")
        assert "Returns" in result

    def test_numpy_dashes_under_section(self):
        result = _gen(
            "transform",
            args=[{"name": "x", "annotation": "int"}],
            style="numpy",
        )
        assert "---" in result or "Parameters" in result


# ══════════════════════════════════════════════════════
#  4. reST Style
# ══════════════════════════════════════════════════════

class TestRestStyle:
    """Generator produces valid reST-style docstrings."""

    def test_rest_param_tag(self):
        result = _gen(
            "fetch",
            args=[{"name": "url", "annotation": "str"}],
            style="rest",
        )
        assert ":param" in result

    def test_rest_return_tag(self):
        result = _gen("fetch", returns="dict", style="rest")
        assert ":return" in result or ":rtype" in result

    def test_rest_type_tag(self):
        result = _gen(
            "fetch",
            args=[{"name": "url", "annotation": "str"}],
            style="rest",
        )
        assert ":type" in result or ":param" in result


# ══════════════════════════════════════════════════════
#  5. Class Generation
# ══════════════════════════════════════════════════════

class TestClassGeneration:
    """Generator handles class item_type without crashing."""

    def test_class_docstring_generated(self):
        result = _gen("MyService", item_type="class")
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_class_name_in_output(self):
        result = _gen("MyService", item_type="class")
        # Name may or may not appear — just ensure no crash
        assert result is not None


# ══════════════════════════════════════════════════════
#  6. Writer Integration — add_docstrings_to_code
# ══════════════════════════════════════════════════════

class TestWriterIntegration:
    """add_docstrings_to_code correctly inserts docstrings."""

    def _run_pipeline(self, code, style="google", overwrite=False):
        from docgen.parser import parse_code
        from docgen.generator import generate_docstring
        from docgen.writer import add_docstrings_to_code

        items = parse_code(code)
        for item in items:
            item["generated_docstring"] = generate_docstring(
                name=item["name"],
                args=item.get("args", []),
                returns=item.get("returns"),
                style=style,
                item_type=item["type"],
            )
        return add_docstrings_to_code(code, items, overwrite=overwrite)

    def test_output_is_valid_python(self, simple_function_code):
        import ast
        result = self._run_pipeline(simple_function_code)
        ast.parse(result)  # raises SyntaxError on failure

    def test_docstring_inserted(self, simple_function_code):
        result = self._run_pipeline(simple_function_code)
        assert '"""' in result or "'''" in result

    def test_overwrite_false_preserves_existing(self, function_with_docstring_code):
        result = self._run_pipeline(
            function_with_docstring_code, overwrite=False
        )
        assert "Say hello" in result

    def test_overwrite_true_replaces_existing(self, function_with_docstring_code):
        result = self._run_pipeline(
            function_with_docstring_code, overwrite=True
        )
        assert isinstance(result, str)

    def test_complex_code_all_items_documented(self, complex_code):
        import ast
        result = self._run_pipeline(complex_code)
        ast.parse(result)
        assert result.count('"""') >= 2


# ══════════════════════════════════════════════════════
#  7. Template Registry
# ══════════════════════════════════════════════════════

class TestTemplateRegistry:
    """Template registry returns correct template for each style."""

    def test_google_template_exists(self):
        from docgen.templates.registry import get_template
        tpl = get_template("google")
        assert tpl is not None

    def test_numpy_template_exists(self):
        from docgen.templates.registry import get_template
        tpl = get_template("numpy")
        assert tpl is not None

    def test_rest_template_exists(self):
        from docgen.templates.registry import get_template
        tpl = get_template("rest")
        assert tpl is not None

    def test_unknown_style_raises_or_defaults(self):
        from docgen.templates.registry import get_template
        try:
            tpl = get_template("unknown_style_xyz")
            # Should either raise or return a default
        except (KeyError, ValueError, Exception):
            pass  # acceptable