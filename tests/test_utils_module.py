"""Test the dtoolcore.utils module."""

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


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
