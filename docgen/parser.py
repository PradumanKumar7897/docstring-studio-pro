import ast
from .infer import infer_type_from_default, infer_return_type


def _get_default_map(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict:
    """
    Build mapping param_name -> default_ast_node
    """
    args = node.args.args
    defaults = node.args.defaults

    default_map = {}
    if defaults:
        start = len(args) - len(defaults)
        for i, default in enumerate(defaults):
            default_map[args[start + i].arg] = default

    return default_map


def parse_code(code: str) -> list[dict]:
    tree = ast.parse(code)
    results = []

    for node in tree.body:

        # ---------------- CLASS ----------------
        if isinstance(node, ast.ClassDef):
            class_info = {
                "type": "class",
                "name": node.name,
                "qualified_name": node.name,
                "docstring": ast.get_docstring(node),
                "lineno": node.lineno,
                "col_offset": node.col_offset,
            }
            results.append(class_info)

            # Parse methods inside class
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    default_map = _get_default_map(child)

                    args_info = []
                    for a in child.args.args:
                        if a.arg == "self":
                            continue

                        ann = ast.unparse(a.annotation) if a.annotation else None
                        inferred = infer_type_from_default(default_map.get(a.arg))

                        args_info.append({
                            "name": a.arg,
                            "type": ann or inferred or "Any"
                        })

                    returns = (
                        ast.unparse(child.returns)
                        if child.returns
                        else infer_return_type(child)
                    )

                    results.append({
                        "type": "function",
                        "name": child.name,
                        "qualified_name": f"{node.name}.{child.name}",
                        "args": args_info,
                        "returns": returns,
                        "docstring": ast.get_docstring(child),
                        "lineno": child.lineno,
                        "col_offset": child.col_offset,
                    })

        # ---------------- TOP LEVEL FUNCTIONS ----------------
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            default_map = _get_default_map(node)

            args_info = []
            for a in node.args.args:
                ann = ast.unparse(a.annotation) if a.annotation else None
                inferred = infer_type_from_default(default_map.get(a.arg))
                args_info.append({"name": a.arg, "type": ann or inferred or "Any"})

            returns = ast.unparse(node.returns) if node.returns else infer_return_type(node)

            results.append({
                "type": "function",
                "name": node.name,
                "qualified_name": node.name,
                "args": args_info,
                "returns": returns,
                "docstring": ast.get_docstring(node),
                "lineno": node.lineno,
                "col_offset": node.col_offset,
            })

    return results


def parse_file(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return parse_code(f.read())
