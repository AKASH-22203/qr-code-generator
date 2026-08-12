import socket
from urllib.parse import urlparse


def normalize_url(value):
    """
    Normalize and validate the basic URL structure.

    Examples:
        google.com
        www.google.com
        https://google.com
        http://github.com

    Returns:
        Normalized URL if structurally valid, otherwise None.
    """

    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    # Add HTTPS when the user doesn't specify a protocol.
    if not value.lower().startswith(("http://", "https://")):
        value = "https://" + value

    try:
        parsed = urlparse(value)

        # Only websites are allowed.
        if parsed.scheme.lower() not in ("http", "https"):
            return None

        # A hostname must exist.
        if not parsed.hostname:
            return None

        hostname = parsed.hostname.lower()

        # Reject whitespace anywhere in the URL.
        if any(character.isspace() for character in value):
            return None

        # Reject malformed hostnames.
        if hostname.startswith(".") or hostname.endswith("."):
            return None

        if ".." in hostname:
            return None

        # localhost is useful for development.
        if hostname != "localhost" and "." not in hostname:
            return None

        # Reject obviously malformed hostnames.
        if len(hostname) > 253:
            return None

        return value

    except (ValueError, TypeError):
        return None


def domain_exists(hostname):
    """
    Check whether the hostname can be resolved using DNS.
    """

    try:
        socket.getaddrinfo(
            hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM
        )

        return True

    except (socket.gaierror, socket.timeout, OSError):
        return False


def validate_url(value, check_dns=True):
    """
    Validate a website URL.

    Returns:
        (True, normalized_url, None)
        or
        (False, None, error_message)
    """

    url = normalize_url(value)

    if not url:
        return (
            False,
            None,
            "Please enter a valid HTTP/HTTPS website URL."
        )

    parsed = urlparse(url)
    hostname = parsed.hostname.lower()

    # Localhost is allowed for development.
    if hostname == "localhost":
        return True, url, None

    if check_dns and not domain_exists(hostname):
        return (
            False,
            None,
            f"The website '{hostname}' could not be found."
        )

    return True, url, None