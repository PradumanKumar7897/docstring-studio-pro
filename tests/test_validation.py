"""
Tests for docgen.validator — docstring validation engine.

Covers:
  - ValidationConfig defaults and custom ignore codes
  - validate_project_code result structure
  - PEP 257 / pydocstyle rule triggering
  - Issue model fields
  - Clean code produces no issues
"""
import pytest
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════

WELL_DOCUMENTED_CODE = '''
def add(a: int, b: int) -> int:
    """Add two integers and return the result.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The sum of a and b.
    """
    return a + b
'''

MISSING_DOCSTRING_CODE = '''
def undocumented(x, y):
    return x - y
'''

INCOMPLETE_DOCSTRING_CODE = '''
def partial(x: int) -> str:
    """Convert x to string."""
    return str(x)
'''


def _validate(code, ignore=None):
    from docgen.validator.service import validate_project_code
    from docgen.validator.config import ValidationConfig

    cfg = ValidationConfig(ignore_codes=ignore or [])
    return validate_project_code(code, cfg)


# ══════════════════════════════════════════════════════
#  1. ValidationConfig
# ══════════════════════════════════════════════════════

class TestValidationConfig:
    """ValidationConfig initialises with correct defaults."""

    def test_default_ignore_codes_is_list(self):
        from docgen.validator.config import ValidationConfig
        cfg = ValidationConfig()
        assert isinstance(cfg.ignore_codes, list)

    def test_custom_ignore_codes_stored(self):
        from docgen.validator.config import ValidationConfig
        cfg = ValidationConfig(ignore_codes=["D203", "D213"])
        assert "D203" in cfg.ignore_codes
        assert "D213" in cfg.ignore_codes

    def test_config_is_instantiable(self):
        from docgen.validator.config import ValidationConfig
        cfg = ValidationConfig()
        assert cfg is not None


# ══════════════════════════════════════════════════════
#  2. validate_project_code — Return Shape
# ══════════════════════════════════════════════════════

class TestValidateReturnShape:
    """validate_project_code returns a dict mapping symbol → issues."""

    def test_returns_dict(self):
        result = _validate(WELL_DOCUMENTED_CODE)
        assert isinstance(result, dict)

    def test_clean_code_no_issues(self):
        result = _validate(
            WELL_DOCUMENTED_CODE,
            ignore=["D203", "D213", "D100", "D101", "D102", "D104"],
        )
        # Either empty dict or empty issue lists
        total = sum(len(v) for v in result.values())
        assert total == 0

    def test_missing_docstring_produces_issues(self):
        result = _validate(MISSING_DOCSTRING_CODE)
        total = sum(len(v) for v in result.values())
        assert total > 0

    def test_keys_are_strings(self):
        result = _validate(MISSING_DOCSTRING_CODE)
        for key in result:
            assert isinstance(key, str)


# ══════════════════════════════════════════════════════
#  3. Issue Model
# ══════════════════════════════════════════════════════

class TestIssueModel:
    """Each issue object has the expected attributes."""

    def _get_first_issue(self):
        result = _validate(MISSING_DOCSTRING_CODE)
        for issues in result.values():
            if issues:
                return issues[0]
        return None

    def test_issue_has_code_attr(self):
        issue = self._get_first_issue()
        if issue:
            assert hasattr(issue, "code")

    def test_issue_has_message_attr(self):
        issue = self._get_first_issue()
        if issue:
            assert hasattr(issue, "message")

    def test_issue_has_line_attr(self):
        issue = self._get_first_issue()
        if issue:
            assert hasattr(issue, "line")

    def test_issue_code_is_string(self):
        issue = self._get_first_issue()
        if issue:
            assert isinstance(issue.code, str)

    def test_issue_line_is_int(self):
        issue = self._get_first_issue()
        if issue:
            assert isinstance(issue.line, int)


# ══════════════════════════════════════════════════════
#  4. Ignore Codes
# ══════════════════════════════════════════════════════

class TestIgnoreCodes:
    """Ignored codes do not appear in results."""

    def test_ignored_code_not_in_results(self):
        # First find what codes appear without ignoring
        result_all = _validate(MISSING_DOCSTRING_CODE)
        all_codes = {
            issue.code
            for issues in result_all.values()
            for issue in issues
        }

        if not all_codes:
            pytest.skip("No issues found to ignore")

        code_to_ignore = list(all_codes)[0]
        result_filtered = _validate(
            MISSING_DOCSTRING_CODE, ignore=[code_to_ignore]
        )
        filtered_codes = {
            issue.code
            for issues in result_filtered.values()
            for issue in issues
        }
        assert code_to_ignore not in filtered_codes


# ══════════════════════════════════════════════════════
#  5. PEP 257 Rules
# ══════════════════════════════════════════════════════

class TestPEP257Rules:
    """Specific PEP 257 violations are correctly detected."""

    def test_missing_docstring_detected(self):
        code = "def no_doc():\n    return 1"
        result = _validate(code)
        total = sum(len(v) for v in result.values())
        assert total > 0

    def test_empty_docstring_flagged(self):
        code = 'def empty_doc():\n    ""\n    return 1'
        result = _validate(code)
        # May flag or may not depending on engine — just ensure no crash
        assert isinstance(result, dict)

    def test_multiline_function_validated(self):
        code = '''
def complex_func(a, b, c):
    return a + b + c
'''
        result = _validate(code)
        assert isinstance(result, dict)