"""Test the dtoolcore package."""


def test_version_is_string():
    import dtoolcore
    assert isinstance(dtoolcore.__version__, str)
