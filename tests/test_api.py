"""Tests for dtool."""


def test_version_is_str():
    from dtoolcore import __version__
    assert isinstance(__version__, str)
