

Run uv run ruff check . — note the rule codes in the output. Look up one or two on https://docs.astral.sh/ruff/rules/ to see the rationale.
Run uv run ruff check --fix . — watch unused imports vanish, imports get sorted, syntax modernized.
Run uv run ruff format . — watch whitespace and quotes normalize.
Re-read the file. The os.path.join call should still trigger PTH118 because that's a suggestion (rewrite to Path), not an automated fix. Fix it by hand.

https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
