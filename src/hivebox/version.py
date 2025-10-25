import importlib.metadata


def print_version() -> None:
    """Print `hivebox` package version."""
    print(importlib.metadata.version("hivebox"))
