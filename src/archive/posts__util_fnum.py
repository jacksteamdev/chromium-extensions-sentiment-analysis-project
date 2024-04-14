def fnum(x: float):
    """Format a number with a fixed number of decimal places."""
    return f"{x:.7f}".rstrip("0").rstrip(".")
