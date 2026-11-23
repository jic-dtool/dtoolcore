"""Regression tests for text file encoding and Windows path helpers."""

import builtins
import os

import pytest

from . import tmp_dir_fixture  # NOQA

NON_ASCII_README = "---\ndescription: Grüße aus Freiburg ✓\n"


@pytest.fixture
def non_utf8_locale(monkeypatch):
    """Simulate a platform whose locale encoding is not UTF-8 (e.g. Windows).

    Files opened in text mode without an explicit encoding fall back to the
    locale encoding, which we pin to cp1252 here.
    """
    import locale

    import dtoolcore.storagebroker

    def cp1252_open(file, mode="r", *args, **kwargs):
        if "b" not in mode and len(args) < 2 and "encoding" not in kwargs:
            kwargs["encoding"] = "cp1252"
        return builtins.open(file, mode, *args, **kwargs)

    monkeypatch.setattr(dtoolcore.storagebroker, "open", cp1252_open,
                        raising=False)
    monkeypatch.setattr(locale, "getpreferredencoding",
                        lambda do_setlocale=True: "cp1252")


@pytest.fixture
def windows_newlines(monkeypatch):
    """Simulate Windows text mode, which writes "\n" as "\r\n".

    Files opened for writing in text mode without an explicit ``newline``
    translate "\n" to ``os.linesep``, which we pin to "\r\n" here.
    """
    import dtoolcore.storagebroker

    def crlf_open(file, mode="r", *args, **kwargs):
        writing = any(m in mode for m in "wax")
        if "b" not in mode and writing and "newline" not in kwargs \
                and len(args) < 3:
            kwargs["newline"] = "\r\n"
        return builtins.open(file, mode, *args, **kwargs)

    monkeypatch.setattr(dtoolcore.storagebroker, "open", crlf_open,
                        raising=False)


def _create_broker(tmp_dir):
    from dtoolcore.storagebroker import DiskStorageBroker

    storagebroker = DiskStorageBroker(os.path.join(tmp_dir, "ds"))
    storagebroker.create_structure()
    return storagebroker


def test_readme_is_written_as_utf8(tmp_dir_fixture, non_utf8_locale):  # NOQA
    """READMEs must be stored as UTF-8 regardless of the platform locale.

    Previously characters outside the locale encoding (here "✓") could not be
    written at all, and others were stored in a platform-dependent encoding.
    """
    storagebroker = _create_broker(tmp_dir_fixture)
    storagebroker.put_readme(NON_ASCII_README)

    with open(storagebroker.get_readme_key(), "rb") as fh:
        assert fh.read() == NON_ASCII_README.encode("utf-8")

    assert storagebroker.get_readme_content() == NON_ASCII_README


def test_utf8_readme_is_read_as_utf8(tmp_dir_fixture, non_utf8_locale):  # NOQA
    """A UTF-8 README (e.g. written on Linux) must be readable on Windows."""
    storagebroker = _create_broker(tmp_dir_fixture)
    with open(storagebroker.get_readme_key(), "wb") as fh:
        fh.write(NON_ASCII_README.encode("utf-8"))

    assert storagebroker.get_readme_content() == NON_ASCII_README


def test_legacy_locale_encoded_readme_is_readable(tmp_dir_fixture, non_utf8_locale):  # NOQA
    """READMEs written by older versions in the locale encoding stay readable.
    """
    legacy_content = "---\ndescription: Grüße\n"
    storagebroker = _create_broker(tmp_dir_fixture)
    with open(storagebroker.get_readme_key(), "wb") as fh:
        fh.write(legacy_content.encode("cp1252"))

    assert storagebroker.get_readme_content() == legacy_content


def test_item_metadata_is_utf8(tmp_dir_fixture, non_utf8_locale):  # NOQA
    """Item metadata fragments round-trip non-ASCII values."""
    storagebroker = _create_broker(tmp_dir_fixture)
    storagebroker.add_item_metadata("file.txt", "comment", "Grüße ✓")
    assert storagebroker.get_item_metadata("file.txt") == {
        "comment": "Grüße ✓"
    }


@pytest.mark.parametrize("path", ["", "/", "/C"])
def test_windows_path_helpers_handle_short_paths(monkeypatch, path):
    """Short paths must not raise IndexError on Windows.

    The check for a leading "/C:" tested ``len(path) >= 2`` and then
    accessed ``path[2]``.
    """
    import dtoolcore.utils

    monkeypatch.setattr(dtoolcore.utils, "IS_WINDOWS", True)

    assert dtoolcore.utils.windows_to_unix_path(path) == path
    assert dtoolcore.utils.unix_to_windows_path(path) == path.replace(
        "/", "\\"
    )


def test_windows_path_helpers_strip_leading_slash_before_drive(monkeypatch):
    import dtoolcore.utils

    monkeypatch.setattr(dtoolcore.utils, "IS_WINDOWS", True)

    assert dtoolcore.utils.windows_to_unix_path("/C:/data") == "C:/data"
    assert dtoolcore.utils.unix_to_windows_path("/C:/data") == "C:\\data"


def test_text_is_written_with_lf_on_windows(tmp_dir_fixture, windows_newlines):  # NOQA
    """Datasets must be byte-identical across platforms.

    Previously text mode wrote "\r\n" line endings on Windows, so README,
    admin metadata and manifest files differed from those written on Linux
    or to object storage.
    """
    storagebroker = _create_broker(tmp_dir_fixture)
    storagebroker.put_readme("---\nkey: value\n")
    storagebroker.put_manifest({"items": {}})

    with open(storagebroker.get_readme_key(), "rb") as fh:
        assert fh.read() == b"---\nkey: value\n"
    with open(storagebroker.get_manifest_key(), "rb") as fh:
        assert b"\r" not in fh.read()


def test_crlf_in_text_is_normalised_to_lf(tmp_dir_fixture):  # NOQA
    """CRLF line endings in content (e.g. a README edited on Windows) are
    stored as LF on every platform."""
    storagebroker = _create_broker(tmp_dir_fixture)
    storagebroker.put_readme("---\r\nkey: value\r\n")

    with open(storagebroker.get_readme_key(), "rb") as fh:
        assert fh.read() == b"---\nkey: value\n"
    assert storagebroker.get_readme_content() == "---\nkey: value\n"


def test_legacy_crlf_file_is_read_with_lf(tmp_dir_fixture):  # NOQA
    """Files written with CRLF by older versions on Windows read as LF."""
    storagebroker = _create_broker(tmp_dir_fixture)
    with open(storagebroker.get_readme_key(), "wb") as fh:
        fh.write(b"---\r\nkey: value\r\n")

    assert storagebroker.get_readme_content() == "---\nkey: value\n"
