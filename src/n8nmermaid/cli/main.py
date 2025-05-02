# src/n8nmermaid/cli/main.py
"""Main CLI application definition using Typer."""

import typer

from n8nmermaid.utils.logging import setup_logging

app = typer.Typer(
    name="n8nmermaid",
    help="Analyzes n8n workflow JSON files and generates Mermaid diagrams or reports.",
    add_completion=False,
)


@app.callback()
def main_callback():
    """Main entry point setup. Called before any command. Configures logging."""
    setup_logging()



if __name__ == "__main__":
    app()
