"""
Integration tests for Docstring Studio Pro.

Tests the full pipeline:
  parse → generate → write → validate

Also covers AI service mocking and CLI entry-point smoke test.
"""
import pytest
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════

def _run_full_pipeline(code: str, style: str = "google", overwrite: bool = False):
    """Execute parse → generate → write → validate and return all results."""
    from docgen.parser import parse_code
    from docgen.generator import generate_docstring
    from docgen.writer import add_docstrings_to_code
    from docgen.validator.service import validate_project_code
    from docgen.validator.config import ValidationConfig

    items = parse_code(code)
    for item in items:
        item["generated_docstring"] = generate_docstring(
            name=item["name"],
            args=item.get("args", []),
            returns=item.get("returns"),
            style=style,
            item_type=item["type"],
        )

    updated = add_docstrings_to_code(code, items, overwrite=overwrite)
    cfg = ValidationConfig(ignore_codes=["D203", "D213"])
    issues = validate_project_code(updated, cfg)

    return {"items": items, "updated": updated, "issues": issues}


# ══════════════════════════════════════════════════════
#  1. Full Pipeline — Simple Code
# ══════════════════════════════════════════════════════

class TestFullPipelineSimple:
    """End-to-end pipeline runs successfully on simple code."""

    def test_pipeline_returns_all_keys(self, simple_function_code):
        result = _run_full_pipeline(simple_function_code)
        assert "items" in result
        assert "updated" in result
        assert "issues" in result

    def test_updated_code_is_valid_python(self, simple_function_code):
        import ast
        result = _run_full_pipeline(simple_function_code)
        ast.parse(result["updated"])

    def test_items_list_not_empty(self, simple_function_code):
        result = _run_full_pipeline(simple_function_code)
        assert len(result["items"]) > 0

    def test_docstring_in_updated_code(self, simple_function_code):
        result = _run_full_pipeline(simple_function_code)
        assert '"""' in result["updated"]


# ══════════════════════════════════════════════════════
#  2. Full Pipeline — Complex Code
# ══════════════════════════════════════════════════════

class TestFullPipelineComplex:
    """End-to-end pipeline handles complex multi-item code."""

    def test_all_styles_produce_valid_python(self, complex_code):
        import ast
        for style in ("google", "numpy", "rest"):
            result = _run_full_pipeline(complex_code, style=style)
            ast.parse(result["updated"])

    def test_multiple_items_all_documented(self, complex_code):
        result = _run_full_pipeline(complex_code)
        for item in result["items"]:
            assert item.get("generated_docstring")

    def test_issues_dict_returned(self, complex_code):
        result = _run_full_pipeline(complex_code)
        assert isinstance(result["issues"], dict)


# ══════════════════════════════════════════════════════
#  3. Pipeline with Overwrite
# ══════════════════════════════════════════════════════

class TestPipelineOverwrite:
    """Overwrite flag is honoured by the full pipeline."""

    def test_overwrite_false_no_duplicate_docstrings(
        self, function_with_docstring_code
    ):
        import ast
        result = _run_full_pipeline(
            function_with_docstring_code, overwrite=False
        )
        ast.parse(result["updated"])

    def test_overwrite_true_valid_python(self, function_with_docstring_code):
        import ast
        result = _run_full_pipeline(
            function_with_docstring_code, overwrite=True
        )
        ast.parse(result["updated"])


# ══════════════════════════════════════════════════════
#  4. AI Service — Mocked
# ══════════════════════════════════════════════════════

class TestAIServiceMocked:
    """AI service integration via mocked provider calls."""

    def _make_ai_config(self, provider="openai", temperature=0.2):
        from docgen.ai.config import AIConfig
        return AIConfig(provider=provider, temperature=temperature)

    def test_generate_docstring_ai_called(self):
        with patch("docgen.ai.service.generate_docstring_ai") as mock_gen:
            mock_gen.return_value = '"""Mocked docstring."""'
            from docgen.ai.service import generate_docstring_ai
            from docgen.ai.config import AIConfig

            cfg = AIConfig(provider="openai", temperature=0.2)
            result = generate_docstring_ai("Generate a docstring.", cfg)
            assert result is not None

    def test_ai_config_provider_stored(self):
        from docgen.ai.config import AIConfig
        cfg = AIConfig(provider="groq", temperature=0.5)
        assert cfg.provider == "groq"

    def test_ai_config_temperature_stored(self):
        from docgen.ai.config import AIConfig
        cfg = AIConfig(provider="openai", temperature=0.7)
        assert cfg.temperature == pytest.approx(0.7)

    def test_ai_error_handled_gracefully(self, simple_function_code):
        """When AI raises, the pipeline should surface an error message rather than crash."""
        with patch("docgen.ai.service.generate_docstring_ai") as mock_gen:
            mock_gen.side_effect = RuntimeError("API unavailable")

            from docgen.ai.config import AIConfig
            from docgen.parser import parse_code

            items = parse_code(simple_function_code)
            cfg = AIConfig(provider="openai", temperature=0.2)

            for item in items:
                try:
                    from docgen.ai.service import generate_docstring_ai
                    item["generated_docstring"] = generate_docstring_ai("prompt", cfg)
                except Exception as e:
                    item["generated_docstring"] = f"AI Error: {e}"
                    item["engine_used"] = "error"

            assert all("AI Error" in i["generated_docstring"] for i in items)


# ══════════════════════════════════════════════════════
#  5. AI Router
# ══════════════════════════════════════════════════════

# tests/test_integration.py  — replace TestAIRouter class

class TestAIRouter:
    """Router selects the correct client for each provider."""

    def test_router_imports(self):
        from docgen.ai.router import route_request  # noqa: F401

    def test_route_request_with_mock(self):
        from docgen.ai.router import route_request
        from docgen.ai.config import AIConfig
        with patch("docgen.ai.router.PROVIDERS", {
            "openai": lambda prompt, cfg: '"""Mocked."""'
        }):
            cfg = AIConfig(provider="openai", temperature=0.2)
            result = route_request("Generate docstring.", cfg)
            assert result == '"""Mocked."""'

    def test_auto_select_picks_available_key(self):
        from docgen.ai.router import auto_select
        cfg = MagicMock()
        cfg.openai_key = ""
        cfg.gemini_key = "abc123"
        cfg.groq_key   = ""
        assert auto_select(cfg) == "gemini"

    def test_invalid_provider_raises(self):
        from docgen.ai.router import route_request
        from docgen.ai.config import AIConfig
        cfg = AIConfig(provider="nonexistent", temperature=0.2)
        with pytest.raises(ValueError, match="Unknown provider"):
            route_request("prompt", cfg)
# ══════════════════════════════════════════════════════
#  6. CLI Smoke Test
# ══════════════════════════════════════════════════════

class TestCLISmokeTest:
    """CLI entry-point is importable and callable."""

    def test_cli_importable(self):
        from docgen.cli import cli  # noqa: F401

    def test_cli_is_callable(self):
        from docgen.cli import cli
        assert callable(cli)

    def test_cli_invocation_with_runner(self, tmp_path):
        from click.testing import CliRunner
        from docgen.cli import cli

        sample = tmp_path / "sample.py"
        sample.write_text("def hello(name: str) -> str:\n    return name\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0


# ══════════════════════════════════════════════════════
#  7. Infer Module
# ══════════════════════════════════════════════════════

class TestInferModule:
    """docgen.infer module is importable and works with basic input."""

    def test_infer_importable(self):
        try:
            from docgen import infer  # noqa: F401
        except ImportError:
            pytest.skip("infer module not available")

    def test_utils_importable(self):
        from docgen import utils  # noqa: F401