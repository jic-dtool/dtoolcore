"""Utility functions for dtoolcore."""

import os
import getpass
import platform


def cross_platform_getuser(is_windows, no_username_in_env):
    """Return the username or "unknown".

    The function returns "unknown" if the platform is windows
    and the username environment variable is not set.
    """
    if is_windows and no_username_in_env:
        return "unknown"
    return getpass.getuser()


def getuser():
    """Return the username."""
    is_windows = platform.system() == "Windows"
    no_username_in_env = os.environ.get("USERNAME") is None
    return cross_platform_getuser(is_windows, no_username_in_env)
