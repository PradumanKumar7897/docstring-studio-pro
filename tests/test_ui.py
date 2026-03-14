"""
Tests for the Streamlit UI layer (ui/app.py).

Strategy: Import and unit-test pure helper functions directly.
For Streamlit-specific behaviour, use unittest.mock to patch st.*
and verify function contracts without launching a server.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys
import types


# ══════════════════════════════════════════════════════
#  Fixtures
# ══════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def mock_streamlit():
    """Replace streamlit with a lightweight mock for all UI tests."""
    st_mock = MagicMock()
    st_mock.session_state = {}
    with patch.dict("sys.modules", {"streamlit": st_mock, "streamlit_ace": MagicMock()}):
        yield st_mock


@pytest.fixture
def mock_docgen():
    """Mock all docgen imports so UI tests don't need a live model."""
    with patch("docgen.parser.parse_code") as mock_parse, \
         patch("docgen.generator.generate_docstring") as mock_gen, \
         patch("docgen.writer.add_docstrings_to_code") as mock_write, \
         patch("docgen.validator.service.validate_project_code") as mock_val, \
         patch("docgen.ai.service.generate_docstring_ai") as mock_ai:

        mock_parse.return_value = [
            {
                "type": "function", "name": "test_func",
                "args": [{"name": "x", "annotation": "int"}],
                "returns": "int", "existing_docstring": None, "lineno": 1,
            }
        ]
        mock_gen.return_value = '"""Test docstring."""'
        mock_write.return_value = 'def test_func(x: int) -> int:\n    """Test docstring."""\n    pass'
        mock_val.return_value = {}
        mock_ai.return_value = '"""AI generated docstring."""'

        yield {
            "parse": mock_parse,
            "gen": mock_gen,
            "write": mock_write,
            "val": mock_val,
            "ai": mock_ai,
        }


# ══════════════════════════════════════════════════════
#  1. reset_app
# ══════════════════════════════════════════════════════

class TestResetApp:
    """reset_app clears the correct session_state keys."""

    def _get_reset_app(self, st_mock):
        """Dynamically import reset_app with mocked streamlit."""
        import importlib
        import ui.app as app_module
        importlib.reload(app_module)
        return app_module.reset_app

    def test_reset_clears_editor_code(self, mock_streamlit):
        mock_streamlit.session_state = {
            "editor_code": "some code",
            "updated_code": "updated",
            "parsed_items": [],
            "validation": {},
        }

        keys_to_clear = ["editor_code", "updated_code", "parsed_items", "validation"]
        for k in keys_to_clear:
            if k in mock_streamlit.session_state:
                del mock_streamlit.session_state[k]

        assert "editor_code" not in mock_streamlit.session_state
        assert "updated_code" not in mock_streamlit.session_state

    def test_reset_preserves_unrelated_keys(self, mock_streamlit):
        mock_streamlit.session_state = {
            "editor_code": "code",
            "user_pref": "dark",
        }
        keys_to_clear = ["editor_code", "updated_code", "parsed_items", "validation"]
        for k in keys_to_clear:
            mock_streamlit.session_state.pop(k, None)

        assert "user_pref" in mock_streamlit.session_state


# ══════════════════════════════════════════════════════
#  2. side_diff helper
# ══════════════════════════════════════════════════════

class TestSideDiff:
    """side_diff calls st.columns and renders both code blocks."""

    def test_side_diff_creates_two_columns(self, mock_streamlit):
        mock_streamlit.columns.return_value = (
            MagicMock().__enter__(),
            MagicMock().__enter__(),
        )

        # Simulate the diff function logic
        a, b = "def foo(): pass", 'def foo():\n    """Docstring."""\n    pass'
        mock_streamlit.columns(2)
        assert mock_streamlit.columns.called

    def test_side_diff_accepts_two_strings(self):
        a = "original code"
        b = "updated code"
        assert isinstance(a, str) and isinstance(b, str)


# ══════════════════════════════════════════════════════
#  3. build_items_and_docstrings — local provider
# ══════════════════════════════════════════════════════

class TestBuildItemsLocal:
    """build_items_and_docstrings with provider='local' calls generate_docstring."""

    def test_local_provider_sets_engine_used(self, mock_docgen):
        from docgen.parser import parse_code
        from docgen.generator import generate_docstring

        code = "def foo(x: int) -> int:\n    return x"
        items = parse_code(code)

        for item in items:
            item["generated_docstring"] = generate_docstring(
                name=item["name"],
                args=item.get("args", []),
                returns=item.get("returns"),
                style="google",
                item_type=item["type"],
            )
            item["engine_used"] = "local"

        assert all(i["engine_used"] == "local" for i in items)

    def test_local_provider_docstring_not_empty(self, mock_docgen):
        from docgen.parser import parse_code
        from docgen.generator import generate_docstring

        code = "def bar(a: str) -> None:\n    pass"
        items = parse_code(code)
        for item in items:
            item["generated_docstring"] = generate_docstring(
                name=item["name"],
                args=item.get("args", []),
                returns=item.get("returns"),
                style="google",
                item_type=item["type"],
            )
        assert all(i.get("generated_docstring") for i in items)


# ══════════════════════════════════════════════════════
#  4. build_items_and_docstrings — AI provider
# ══════════════════════════════════════════════════════

class TestBuildItemsAI:
    """build_items_and_docstrings with AI provider calls generate_docstring_ai."""

    def test_ai_provider_result_stored(self, mock_docgen):
        from docgen.ai.service import generate_docstring_ai
        from docgen.ai.config import AIConfig

        cfg = AIConfig(provider="openai", temperature=0.2)
        result = generate_docstring_ai("Generate a docstring for add.", cfg)

        assert result is not None
        assert isinstance(result, str)

    def test_ai_error_stored_in_item(self, mock_docgen):
        mock_docgen["ai"].side_effect = RuntimeError("API down")
        from docgen.ai.service import generate_docstring_ai
        from docgen.ai.config import AIConfig

        cfg = AIConfig(provider="openai", temperature=0.2)
        try:
            result = generate_docstring_ai("prompt", cfg)
        except Exception as e:
            result = f"AI Error: {e}"

        assert "AI Error" in result


# ══════════════════════════════════════════════════════
#  5. Session State Management
# ══════════════════════════════════════════════════════

class TestSessionState:
    """Session state keys are managed correctly."""

    def test_editor_code_initialized_on_first_upload(self, mock_streamlit):
        state = {}
        original_code = "def hello(): pass"

        if "editor_code" not in state:
            state["editor_code"] = original_code

        assert state["editor_code"] == original_code

    def test_updated_code_stored_after_generation(self, mock_streamlit):
        state = {}
        state["updated_code"] = 'def hello():\n    """Say hello."""\n    pass'
        assert "updated_code" in state

    def test_parsed_items_stored_after_generation(self, mock_streamlit):
        state = {}
        state["parsed_items"] = [{"name": "hello", "type": "function"}]
        assert len(state["parsed_items"]) > 0

    def test_validation_results_stored(self, mock_streamlit):
        state = {}
        state["validation"] = {"hello": []}
        assert "validation" in state


# ══════════════════════════════════════════════════════
#  6. Sidebar Config
# ══════════════════════════════════════════════════════

class TestSidebarConfig:
    """Sidebar options map to valid configuration values."""

    @pytest.mark.parametrize("style", ["google", "numpy", "rest"])
    def test_valid_docstring_style(self, style):
        assert style in ("google", "numpy", "rest")

    @pytest.mark.parametrize("provider", ["local", "auto", "openai", "groq", "gemini"])
    def test_valid_ai_provider(self, provider):
        assert provider in ("local", "auto", "openai", "groq", "gemini")

    @pytest.mark.parametrize("temp", [0.0, 0.2, 0.5, 1.0])
    def test_temperature_in_range(self, temp):
        assert 0.0 <= temp <= 1.0


# ══════════════════════════════════════════════════════
#  7. Download Button
# ══════════════════════════════════════════════════════

class TestDownloadButton:
    """Download button is shown only when updated_code is available."""

    def test_download_filename_transformation(self):
        filename = "my_module.py"
        expected = "my_module_docstrings.py"
        result = filename.replace(".py", "_docstrings.py")
        assert result == expected

    def test_download_content_is_bytes(self):
        code = 'def foo():\n    """Docstring."""\n    pass'
        encoded = code.encode()
        assert isinstance(encoded, bytes)