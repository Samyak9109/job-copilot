def truncate(text: str, n: int) -> str:
    """Trim text to n chars with an ellipsis marker. Shared preview helper."""
    text = text or ""
    return text[:n] + (" ..." if len(text) > n else "")
