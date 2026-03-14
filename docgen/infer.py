import ast


def infer_type_from_default(default_node) -> str | None:
    """
    Infer a parameter type from its default value.
    Example:
        x=1 -> int
        y=1.2 -> float
        z=True -> bool
        name="hi" -> str
        items=[] -> list
        data={} -> dict
        t=None -> Optional[Any]
    """
    if default_node is None:
        return None

    if isinstance(default_node, ast.Constant):
        v = default_node.value
        if v is None:
            return "Optional[Any]"
        if isinstance(v, bool):
            return "bool"
        if isinstance(v, int):
            return "int"
        if isinstance(v, float):
            return "float"
        if isinstance(v, str):
            return "str"

    if isinstance(default_node, ast.List):
        return "list"
    if isinstance(default_node, ast.Tuple):
        return "tuple"
    if isinstance(default_node, ast.Dict):
        return "dict"
    if isinstance(default_node, ast.Set):
        return "set"

    if isinstance(default_node, ast.Call):
        # e.g. list(), dict(), set()
        if isinstance(default_node.func, ast.Name):
            return default_node.func.id

    return "Any"


def infer_return_type(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """
    Infer return type by scanning return statements.
    This is not perfect but works well for many cases.
    """
    found_types = set()

    for node in ast.walk(func_node):
        if isinstance(node, ast.Return):
            value = node.value

            if value is None:
                found_types.add("None")
                continue

            if isinstance(value, ast.Constant):
                v = value.value
                if v is None:
                    found_types.add("None")
                elif isinstance(v, bool):
                    found_types.add("bool")
                elif isinstance(v, int):
                    found_types.add("int")
                elif isinstance(v, float):
                    found_types.add("float")
                elif isinstance(v, str):
                    found_types.add("str")
                else:
                    found_types.add("Any")

            elif isinstance(value, ast.List):
                found_types.add("list")
            elif isinstance(value, ast.Tuple):
                found_types.add("tuple")
            elif isinstance(value, ast.Dict):
                found_types.add("dict")
            elif isinstance(value, ast.Set):
                found_types.add("set")
            else:
                found_types.add("Any")

    if not found_types:
        return None

    if len(found_types) == 1:
        return list(found_types)[0]

    return f"Union[{', '.join(sorted(found_types))}]"
