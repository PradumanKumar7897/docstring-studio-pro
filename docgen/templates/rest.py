from .base import DocstringTemplate


class RestTemplate(DocstringTemplate):
    def render_function(self, name: str, summary: str, args: list, returns: str | None) -> str:
        args_block = ""
        if args:
            lines = []
            for a in args:
                lines.append(f":param {a['name']}: Description.")
                lines.append(f":type {a['name']}: {a.get('type','Any')}")
            args_block = "\n".join(lines) + "\n"

        returns_block = ""
        if returns is not None:
            returns_block = f":return: Description.\n:rtype: {returns}\n"

        return f'''"""
{summary}

{args_block}{returns_block}"""'''

    def render_class(self, name: str, summary: str) -> str:
        return f'''"""
{summary}
"""'''
