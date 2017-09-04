"""Utility functions for dtoolcore."""

import os
import errno
import getpass
import hashlib
import platform
import binascii
import base64


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


def sha1_hexdigest(input_string):
    """Return hex digest of the sha1sum of the input_string."""

    byte_string = input_string.encode()

    return hashlib.sha1(byte_string).hexdigest()


def base64_to_hex(input_string):
    """Retun the hex encoded version of the base64 encoded input string."""

    return binascii.hexlify(base64.b64decode(input_string)).decode()


def generate_identifier(handle):
    """Return identifier from a ProtoDataSet handle."""
    return sha1_hexdigest(handle)


def mkdir_parents(path):
    """Create the given directory path.
    This includes all necessary parent directories. Does not raise an error if
    the directory already exists.
    :param path: path to create
    """

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise
