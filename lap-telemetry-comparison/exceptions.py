class LaptimeMissingError(Exception):
    """Raised when a lap's time is missing and cannot be reconstructed from sector times."""
    pass