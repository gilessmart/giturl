class GitUrlError(Exception):
    """Indicates an issue due to invalid operation 
    e.g. the repo was not in a suitable state to generate a URL, invalid parameters were supplied etc."""
    pass