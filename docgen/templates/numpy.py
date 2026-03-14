from .base import DocstringTemplate


class NumpyTemplate(DocstringTemplate):
    def render_function(self, name: str, summary: str, args: list, returns: str | None) -> str:
        params_block = ""
        if args:
            params_lines = []
            for a in args:
                params_lines.append(
                    f"{a['name']} : {a.get('type','Any')}\n    Description."
                )
            params_block = "Parameters\n----------\n" + "\n".join(params_lines) + "\n\n"

        returns_block = ""
        if returns is not None:
            returns_block = (
                "Returns\n-------\n"
                + f"{returns}\n    Description.\n"
            )

        return f'''"""
{summary}

{params_block}{returns_block}"""'''

    def render_class(self, name: str, summary: str) -> str:
        return f'''"""
{summary}
"""'''
