"""Utility functions for dtoolcore."""

import os
import errno
import getpass
import hashlib
import json
import platform
import binascii
import base64
import datetime
import re

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse


DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/dtool/dtool.json")

MAX_NAME_LENGTH = 80
NAME_VALID_CHARS_LIST = ["0-9", "a-z", "A-Z", "-", "_", "."]
NAME_VALID_CHARS_STR = "".join(NAME_VALID_CHARS_LIST)
NAME_VALID_CHARS_REGEX = re.compile(r"^[{}]+$".format(NAME_VALID_CHARS_STR))


def generous_parse_uri(uri):
    """Return a urlparse.ParseResult object with the results of parsing the
    given URI. This has the same properties as the result of parse_uri.

    When passed a relative path, it determines the absolute path, sets the
    scheme to file, the netloc to localhost and returns a parse of the result.
    """

    parse_result = urlparse(uri)

    if parse_result.scheme == '':
        abspath = os.path.abspath(parse_result.path)
        fixed_uri = "file://localhost{}".format(abspath)
        parse_result = urlparse(fixed_uri)

    return parse_result


def sanitise_uri(uri):
    """Return fully qualified uri from the input, which might be a relpath."""

    return urlunparse(generous_parse_uri(uri))


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


def get_config_value(key, config_path=None, default=None):
    """Get a configuration value.

    Preference:
    1. From environment
    2. From JSON configuration file supplied in ``config_path`` argument
    3. The default supplied to the function

    :param key: name of lookup value
    :param config_path: path to JSON configuration file
    :param default: default fall back value
    :returns: value associated with the key
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    # Start by setting default value
    value = default

    # Update from config file
    if os.path.isfile(config_path):
        with open(config_path, "r") as fh:
            config = json.load(fh)
            value = config.get(key, value)

    # Update from environment variable
    value = os.environ.get(key, value)
    return value


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


def timestamp(datetime_obj):
    """Return Unix timestamp as float.

    The number of seconds that have elapsed since January 1, 1970.
    """
    start_of_time = datetime.datetime(1970, 1, 1)
    diff = datetime_obj - start_of_time
    return diff.total_seconds()


def name_is_valid(name):
    """Return True if the dataset name is valid.

    The name can only be 80 characters long.
    Valid characters: Alpha numeric characters [0-9a-zA-Z]
    Valid special characters: - _ .
    """
    # The name can only be 80 characters long.
    if len(name) > MAX_NAME_LENGTH:
        return False
    return bool(NAME_VALID_CHARS_REGEX.match(name))
