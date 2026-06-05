"""Allows `python -m expense_pipeline ...` to work by delegating to the CLI."""

from expense_pipeline.cli import main

if __name__ == "__main__":
    main()
