import click
from .parser import parse_file
from .generator import generate_docstring
from .writer import add_docstrings_to_code


@click.group()
def cli():
    """DocGen - Professional Docstring Generator CLI"""
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
def scan(filepath):
    """Scan a file and print extracted metadata"""
    items = parse_file(filepath)
    for i in items:
        click.echo(i)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--style", type=click.Choice(["google", "numpy", "rest"]), default="google")
@click.option("--write", is_flag=True, help="Write changes back into file")
@click.option("--overwrite", is_flag=True, help="Overwrite existing docstrings")
def generate(filepath, style, write, overwrite):
    """Generate docstrings for a Python file"""

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    items = parse_file(filepath)

    for info in items:
        if info["type"] == "function":
            info["generated_docstring"] = generate_docstring(
                name=info["name"],
                args=info.get("args", []),
                returns=info.get("returns"),
                style=style,
                item_type="function",
            )
        elif info["type"] == "class":
            info["generated_docstring"] = generate_docstring(
                name=info["name"],
                args=[],
                returns=None,
                style=style,
                item_type="class",
            )

    updated_code = add_docstrings_to_code(code, items, overwrite=overwrite)

    if write:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(updated_code)
        click.echo(f"✅ Updated file written: {filepath}")
    else:
        click.echo(updated_code)
