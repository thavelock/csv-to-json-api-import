"""Primary logic for the CLI Tool
"""

# ===== IMPORTS =====

import json

import requests
import typer
from rich import print
from typing_extensions import Annotated

# ===== CONSTANTS =====



# ===== GLOBALS =====

app = typer.Typer(add_completion=False)
state = {"verbose": False}

# ===== METHODS =====

@app.command()
def main(
    sample_arg:
        Annotated[
            str,
            typer.Argument(
                help='Sample argument',
                envvar='SAMPLE_ENV_VAR')]):
    return

def run():
    """Run the defined typer CLI app
    """
    app()
