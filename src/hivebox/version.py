import importlib.metadata


def version() -> str:
    """Return `hivebox` package version."""
    return importlib.metadata.version("hivebox")
