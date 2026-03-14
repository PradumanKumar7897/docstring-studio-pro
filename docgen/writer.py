import libcst as cst
from .utils import clean_docstring_text


def add_docstrings_to_code(code: str, items_info: list, overwrite: bool = False) -> str:
    """
    Insert docstrings using LibCST (safe, formatting-preserving).

    Args:
        code: original code
        items_info: list of metadata dicts with generated_docstring
        overwrite: if True, replace existing docstrings

    Returns:
        updated code
    """

    info_map = {}
    for info in items_info:
        qn = info.get("qualified_name")
        if qn and info.get("generated_docstring"):
            info_map[qn] = info

    class Inserter(cst.CSTTransformer):
        def __init__(self):
            self.class_stack = []

        def _make_doc_stmt(self, doc: str) -> cst.SimpleStatementLine:
            content = clean_docstring_text(doc)
            return cst.SimpleStatementLine(
                body=[cst.Expr(value=cst.SimpleString(f'"""{content}"""'))]
            )

        def _has_docstring(self, suite: cst.BaseSuite) -> bool:
            if not suite.body:
                return False
            first = suite.body[0]
            if not isinstance(first, cst.SimpleStatementLine):
                return False
            if not first.body:
                return False
            expr = first.body[0]
            return isinstance(expr, cst.Expr) and isinstance(expr.value, cst.SimpleString)

        def _remove_existing_docstring(self, suite: cst.BaseSuite) -> list:
            if not suite.body:
                return list(suite.body)
            if self._has_docstring(suite):
                return list(suite.body[1:])
            return list(suite.body)

        # ---------- CLASS ----------
        def visit_ClassDef(self, node: cst.ClassDef):
            self.class_stack.append(node.name.value)
            return True

        def leave_ClassDef(self, original_node, updated_node):
            class_name = self.class_stack.pop()
            qn = class_name

            info = info_map.get(qn)
            if not info:
                return updated_node

            suite = updated_node.body

            if self._has_docstring(suite) and not overwrite:
                return updated_node

            new_body = self._remove_existing_docstring(suite) if overwrite else list(suite.body)
            doc_stmt = self._make_doc_stmt(info["generated_docstring"])

            updated_suite = suite.with_changes(body=[doc_stmt] + new_body)
            return updated_node.with_changes(body=updated_suite)

        # ---------- FUNCTIONS ----------
        def leave_FunctionDef(self, original_node, updated_node):
            if self.class_stack:
                qn = f"{self.class_stack[-1]}.{original_node.name.value}"
            else:
                qn = original_node.name.value

            info = info_map.get(qn)
            if not info:
                return updated_node

            suite = updated_node.body

            if self._has_docstring(suite) and not overwrite:
                return updated_node

            new_body = self._remove_existing_docstring(suite) if overwrite else list(suite.body)
            doc_stmt = self._make_doc_stmt(info["generated_docstring"])

            updated_suite = suite.with_changes(body=[doc_stmt] + new_body)
            return updated_node.with_changes(body=updated_suite)

        def leave_AsyncFunctionDef(self, original_node, updated_node):
            if self.class_stack:
                qn = f"{self.class_stack[-1]}.{original_node.name.value}"
            else:
                qn = original_node.name.value

            info = info_map.get(qn)
            if not info:
                return updated_node

            suite = updated_node.body

            if self._has_docstring(suite) and not overwrite:
                return updated_node

            new_body = self._remove_existing_docstring(suite) if overwrite else list(suite.body)
            doc_stmt = self._make_doc_stmt(info["generated_docstring"])

            updated_suite = suite.with_changes(body=[doc_stmt] + new_body)
            return updated_node.with_changes(body=updated_suite)

    module = cst.parse_module(code)
    updated = module.visit(Inserter())
    return updated.code
