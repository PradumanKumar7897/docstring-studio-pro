import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
Shared pytest fixtures for Docstring Studio Pro test suite.
"""
import pytest


# ─────────────────────────── Code Samples ────────────────────────────

SIMPLE_FUNCTION = '''
def add(a: int, b: int) -> int:
    return a + b
'''

FUNCTION_WITH_DOCSTRING = '''
def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}"
'''

FUNCTION_NO_ARGS = '''
def get_version() -> str:
    return "1.0.0"
'''

SIMPLE_CLASS = '''
class Calculator:
    def __init__(self, precision: int = 2):
        self.precision = precision

    def multiply(self, x: float, y: float) -> float:
        return round(x * y, self.precision)
'''

COMPLEX_CODE = '''
from typing import List, Optional

class DataProcessor:
    def __init__(self, config: dict):
        self.config = config
        self._cache = {}

    def process(self, data: List[dict], strict: bool = False) -> Optional[List[dict]]:
        if not data:
            return None
        return [self._transform(item) for item in data]

    def _transform(self, item: dict) -> dict:
        return {k: str(v) for k, v in item.items()}

def standalone_helper(path: str, encoding: str = "utf-8") -> str:
    with open(path, encoding=encoding) as f:
        return f.read()
'''

INVALID_PYTHON = '''
def broken(:
    pass ===
'''

EMPTY_CODE = ""

ASYNC_FUNCTION = '''
import asyncio

async def fetch_data(url: str, timeout: int = 30) -> dict:
    await asyncio.sleep(0.1)
    return {"url": url, "status": 200}
'''



# ─────────────────────────── Fixtures ────────────────────────────────

@pytest.fixture
def simple_function_code():
    return SIMPLE_FUNCTION

@pytest.fixture
def function_with_docstring_code():
    return FUNCTION_WITH_DOCSTRING

@pytest.fixture
def simple_class_code():
    return SIMPLE_CLASS

@pytest.fixture
def complex_code():
    return COMPLEX_CODE

@pytest.fixture
def invalid_python_code():
    return INVALID_PYTHON

@pytest.fixture
def empty_code():
    return EMPTY_CODE

@pytest.fixture
def async_function_code():
    return ASYNC_FUNCTION

@pytest.fixture
def function_no_args_code():
    return FUNCTION_NO_ARGS

@pytest.fixture
def sample_parsed_item():
    return {
        "type": "function",
        "name": "add",
        "args": [
            {"name": "a", "annotation": "int"},
            {"name": "b", "annotation": "int"},
        ],
        "returns": "int",
        "existing_docstring": None,
        "lineno": 2,
    }

@pytest.fixture
def sample_class_item():
    return {
        "type": "class",
        "name": "Calculator",
        "args": [],
        "returns": None,
        "docstring": None,
        "lineno": 1,
    }