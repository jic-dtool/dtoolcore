"""Test the dtoolcore.utils module."""

import os
import sys
import json

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from . import tmp_dir_fixture  # NOQA
from . import tmp_env_var


def test_sha1_hexdigest():
    from dtoolcore.utils import sha1_hexdigest
    string = "Test me"

    assert sha1_hexdigest(string) == "9940674fb235beddae40df565cbfc688b824b362"


def test_generate_identifier():
    from dtoolcore.utils import generate_identifier
    string = "Test me"

    assert generate_identifier(handle=string) ==  \
        "9940674fb235beddae40df565cbfc688b824b362"


def test_cross_platform_getuser_windows_and_no_username_env_var():
    from dtoolcore.utils import cross_platform_getuser
    import getpass
    getpass.getuser = MagicMock(return_value="user1")
    assert cross_platform_getuser(True, True) == "unknown"
    assert getpass.getuser.not_called()


def test_cross_platform_getuser_windows_and_username_env_var():
    from dtoolcore.utils import cross_platform_getuser
    import getpass
    getpass.getuser = MagicMock(return_value="user1")
    assert cross_platform_getuser(True, False) == "user1"
    assert getpass.getuser.called_once()


def test_cross_platform_getuser_not_windows_and_username_env_var():
    from dtoolcore.utils import cross_platform_getuser
    import getpass
    getpass.getuser = MagicMock(return_value="user1")
    assert cross_platform_getuser(False, False) == "user1"
    assert getpass.getuser.called_once()


def test_cross_platform_getuser_not_windows_and_no_username_env_var():
    from dtoolcore.utils import cross_platform_getuser
    import getpass
    getpass.getuser = MagicMock(return_value="user1")
    assert cross_platform_getuser(False, True) == "user1"
    assert getpass.getuser.called_once()


def test_getuser():
    import dtoolcore.utils
    dtoolcore.utils.cross_platform_getuser = MagicMock(return_value="user1")
    assert dtoolcore.utils.getuser() == "user1"
    assert dtoolcore.utils.cross_platform_getuser.called_once()


def test_base64_to_hex():
    from dtoolcore.utils import base64_to_hex

    input_string = "86aJiAkXSLnTuXcSVW8/TVdYTbp2of+veyzp3a3A3uA="
    e = "f3a68988091748b9d3b97712556f3f4d57584dba76a1ffaf7b2ce9ddadc0dee0"

    assert base64_to_hex(input_string) == e


def test_write_config_value_to_file(tmp_dir_fixture):  # NOQA
    from dtoolcore.utils import write_config_value_to_file
    config_path = os.path.join(tmp_dir_fixture, "my.conf")
    assert not os.path.isfile(config_path)

    value = write_config_value_to_file("my-key", "my-value", config_path)
    assert value == "my-value"
    assert os.path.isfile(config_path)

    with open(config_path) as fh:
        config = json.load(fh)
    assert config == {"my-key": "my-value"}

    value = write_config_value_to_file("my-key", "updated-value", config_path)
    assert value == "updated-value"

    with open(config_path) as fh:
        config = json.load(fh)
    assert config == {"my-key": "updated-value"}

    write_config_value_to_file("another-key", "value", config_path)

    with open(config_path) as fh:
        config = json.load(fh)
    assert config == {
        "my-key": "updated-value",
        "another-key": "value"
    }

    # Ensure that the file has 600 permissions.
    if sys.platform != "win32":
        # Don't do this check on windows
        assert os.stat(config_path).st_mode == 33216


def test_get_config_value():
    from dtoolcore.utils import get_config_value
    value = get_config_value(
        key="MY_KEY",
        config_path=None,
        default="hello"
    )
    assert value == "hello"


def test_get_config_dict_from_file(tmp_dir_fixture):  # NOQA
    from dtoolcore.utils import _get_config_dict_from_file

    # Test default file (~/.config/dtool/dtool.json).
    assert isinstance(_get_config_dict_from_file(), dict)

    config_path = os.path.join(tmp_dir_fixture, "my.conf")

    # Test when config file is missing.
    assert {} == _get_config_dict_from_file(
        config_path=config_path
    )

    config = {"MY_KEY": "from_file"}
    with open(config_path, "w") as fh:
        json.dump(config, fh)

    # Test when config file exists.
    assert {"MY_KEY": "from_file"} == _get_config_dict_from_file(
        config_path=config_path
    )


def test_get_config_value_from_file(tmp_dir_fixture):  # NOQA
    from dtoolcore.utils import get_config_value, get_config_value_from_file

    config_path = os.path.join(tmp_dir_fixture, "my.conf")

    # Test when config file is missing.
    assert get_config_value_from_file(
        key="MY_KEY",
        config_path=config_path
    ) is None

    config = {"MY_KEY": "from_file"}
    with open(config_path, "w") as fh:
        json.dump(config, fh)

    # Test when config file exists.
    assert "from_file" == get_config_value_from_file(
        key="MY_KEY",
        config_path=config_path
    )

    # Test use in get_config_value function.
    value = get_config_value(
        key="MY_KEY",
        config_path=config_path,
        default="hello"
    )
    assert value == "from_file"


def test_get_config_value_from_env(tmp_dir_fixture):  # NOQA
    from dtoolcore.utils import get_config_value

    config = {"MY_KEY": "from_file"}
    config_path = os.path.join(tmp_dir_fixture, "my.conf")
    with open(config_path, "w") as fh:
        json.dump(config, fh)

    with tmp_env_var("MY_KEY", "from_env"):
        value = get_config_value(
            key="MY_KEY",
            config_path=config_path,
            default="hello"
        )
    assert value == "from_env"


def test_name_is_valid():

    from dtoolcore.utils import name_is_valid

    assert name_is_valid("this-is-a-good-name")
    assert name_is_valid("this_is_a_good_name")
    assert name_is_valid("0-name-1-can-contain-numbers-2")
    assert name_is_valid("this.is.a.good.name")
    assert name_is_valid("THIS-IS-A-GOOD-NAME")

    # Name can only be 80 chars long.
    assert name_is_valid("x" * 80)
    assert not name_is_valid("x" * 81)

    assert not name_is_valid("/root/this-is-a-bad-name")
    assert not name_is_valid("th\is-is-a-bad-name")  # NOQA
    assert not name_is_valid("th\\is-is-a-bad-name")
    assert not name_is_valid("th\nis-is-a-bad-name")
    assert not name_is_valid("{this-is-a-bad-name}")
    assert not name_is_valid("^this^is-a-bad-name")
    assert not name_is_valid("<this<is-a-bad-name>")
    assert not name_is_valid("`this`is-a-bad-name")
    assert not name_is_valid("@this@is-a-bad-name")
    assert not name_is_valid("&this&is-a-bad-name")
    assert not name_is_valid(",this,is-a-bad-name")
    assert not name_is_valid("?this?is-a-bad-name")
    assert not name_is_valid("$this$is-a-bad-name")
    assert not name_is_valid("=this=is-a-bad-name")
    assert not name_is_valid("+this+is-a-bad-name")
    assert not name_is_valid(" this is-a-bad-name")
    assert not name_is_valid(" this is a bad name")
    assert not name_is_valid(":this:is-a-bad-name")
    assert not name_is_valid("this-is-a-bad-name+")


def test_relpath_to_handle():
    from dtoolcore.utils import relpath_to_handle
    assert relpath_to_handle("subdir/test.txt") == "subdir/test.txt"
    assert relpath_to_handle("./subdir/test.txt") == "subdir/test.txt"
    assert relpath_to_handle(
        "subdir\\test.txt",
        is_windows=True) == "subdir/test.txt"
