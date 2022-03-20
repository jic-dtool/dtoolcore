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
import socket
import logging

try:
    from urlparse import urlparse, urlunparse
except ImportError:
    from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

IS_WINDOWS = False
if platform.system() == "Windows":
    IS_WINDOWS = True

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/dtool/dtool.json")
DEFAULT_CACHE_PATH = os.path.expanduser("~/.cache/dtool")

MAX_NAME_LENGTH = 80
NAME_VALID_CHARS_LIST = ["0-9", "a-z", "A-Z", "-", "_", "."]
NAME_VALID_CHARS_STR = "".join(NAME_VALID_CHARS_LIST)
NAME_VALID_CHARS_REGEX = re.compile(r"^[{}]+$".format(NAME_VALID_CHARS_STR))


def windows_to_unix_path(win_path):
    """Return Unix path."""
    logger.debug("In windows_to_unix_path...")
    logger.debug("windows_to_unix_path.input_win_path: {}".format(win_path))
    unix_path = win_path.replace("\\", "/")

    # Deal with Windows path defect where path has incorrect starting /, e.g.
    # /C:/some/path.
    if IS_WINDOWS and len(unix_path) >=2  and unix_path[0] == "/" and unix_path[2] == ":":  # NOQA
        unix_path = unix_path[1:]

    logger.debug("windows_to_unix_path.return: {}".format(unix_path))
    return unix_path


def unix_to_windows_path(unix_path):
    """Return Windows path."""
    logger.debug("In unix_to_windows_path...")
    logger.debug("unix_to_windows_path.input_unix_path: {}".format(unix_path))

    # Deal with Windows path defect where path has incorrect starting /, e.g.
    # /C:/some/path.
    if IS_WINDOWS  and len(unix_path) >= 2  and unix_path[0] == "/" and unix_path[2] == ":":  # NOQA
        unix_path = unix_path[1:]

    win_path = unix_path.replace("/", "\\")
    logger.debug("unix_to_windows_path.return: {}".format(win_path))
    return win_path


def generous_parse_uri(uri):
    """Return a urlparse.ParseResult object with the results of parsing the
    given URI. This has the same properties as the result of parse_uri.

    When passed a relative path, it determines the absolute path, sets the
    scheme to file, the netloc to localhost and returns a parse of the result.
    """
    logger.debug("In generous_pase_uri...")
    logger.debug("generous_pase_uri.input_uri: {}".format(uri))

    parse_result = urlparse(uri)

    IS_WINDOWS_DRIVE_LETTER = len(parse_result.scheme) == 1

    if parse_result.scheme == '' or IS_WINDOWS_DRIVE_LETTER:
        abspath = os.path.abspath(parse_result.path)
        fixed_uri = "file://{}{}".format(
            socket.gethostname(),
            abspath
        )
        if IS_WINDOWS:
            abspath = windows_to_unix_path(abspath)
            if IS_WINDOWS_DRIVE_LETTER:
                abspath = parse_result.scheme.upper() + abspath[1:]
            fixed_uri = "file:///{}".format(abspath)
        parse_result = urlparse(fixed_uri)

    logger.debug("generouse_pase_uri.return: {}".format(parse_result))
    return parse_result


def sanitise_uri(uri):
    """Return fully qualified uri from the input, which might be a relpath."""
    logger.debug("In sanitise_uri...")
    logger.debug("sanitise_uri.input_uri: {}".format(uri))
    logger.debug("sanitise_uri.calling.utils.generouse_parse_uri")
    uri = urlunparse(generous_parse_uri(uri))
    logger.debug("sanitise_uri.return: {}".format(uri))
    return uri


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


def _get_config_dict_from_file(config_path=None):
    """Return value if key exists in file.

    Return empty string ("") if key or file does not exist.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    # Default (empty) content will be used if config file does not exist.
    config_content = {}

    # If the config file exists we use that content.
    if os.path.isfile(config_path):
        with open(config_path) as fh:
            config_content = json.load(fh)

    return config_content


def write_config_value_to_file(key, value, config_path=None):
    """Write key/value pair to config file.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    # Get existing config.
    config = _get_config_dict_from_file(config_path)

    # Add/update the key/value pair.
    config[key] = value

    # Create parent directories if they are missing.
    mkdir_parents(os.path.dirname(config_path))

    # Write the content
    with open(config_path, "w") as fh:
        json.dump(config, fh, sort_keys=True, indent=2)

    # Set 600 permissions on the config file.
    os.chmod(config_path, 33216)

    return get_config_value_from_file(key, config_path)


def get_config_value_from_file(key, config_path=None, default=None):
    """Return value if key exists in file.

    Return default if key not in config.
    """
    config = _get_config_dict_from_file(config_path)
    if key not in config:
        return default
    return config[key]


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
    value = get_config_value_from_file(
        key=key,
        config_path=config_path,
        default=value
    )

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


def relpath_to_handle(relpath, is_windows=False):
    """Return handle from relpath.

    Handles are Unix style relpaths.
    Converts Windows relpath to Unix style relpath.
    Strips "./" prefix.
    """
    if is_windows:
        relpath = windows_to_unix_path(relpath)
    if relpath.startswith("./"):
        relpath = relpath[2:]
    return relpath


def handle_to_osrelpath(handle, is_windows=False):
    """Return OS specific relpath from handle."""
    directories = handle.split("/")
    if is_windows:
        return "\\".join(directories)
    return "/".join(directories)
