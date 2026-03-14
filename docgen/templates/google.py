from .base import DocstringTemplate


class GoogleTemplate(DocstringTemplate):
    def render_function(self, name: str, summary: str, args: list, returns: str | None) -> str:
        args_block = ""
        if args:
            arg_lines = []
            for a in args:
                arg_lines.append(f"    {a['name']} ({a.get('type','Any')}): Description.")
            args_block = "Args:\n" + "\n".join(arg_lines) + "\n\n"

        returns_block = ""
        if returns is not None:
            returns_block = f"Returns:\n    {returns}: Description.\n"

        return f'''"""
{summary}

{args_block}{returns_block}"""'''

    def render_class(self, name: str, summary: str) -> str:
        return f'''"""
{summary}
"""'''
