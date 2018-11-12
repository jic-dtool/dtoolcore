"""Test filehasher API."""

import os

from . import TEST_SAMPLE_DATA


def test_sha1sum_hexdigest():
    from dtoolcore.filehasher import sha1sum_hexdigest
    expected = "09648d19e11f0b20e5473594fc278afbede3c9a4"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'tiny.png')
    actual = sha1sum_hexdigest(test_file)
    assert actual == expected


def test_md5sum_hexdigest():
    from dtoolcore.filehasher import md5sum_hexdigest
    expected = "dc73192d2f81d7009ce5a1ee7bad5755"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'tiny.png')
    actual = md5sum_hexdigest(test_file)
    assert actual == expected


def test_md5sum_digest():
    from dtoolcore.filehasher import md5sum_digest
    from base64 import b64encode
    expected = "3HMZLS+B1wCc5aHue61XVQ=="
    test_file = os.path.join(TEST_SAMPLE_DATA, 'tiny.png')
    actual = b64encode(md5sum_digest(test_file)).decode("utf-8")
    assert actual == expected, actual


def test_sha256sum_hexdigest():
    from dtoolcore.filehasher import sha256sum_hexdigest
    e = "98a64a1f16995c6ab9fce541e824e5727cbe63079614ffd7665ab1a8b7cd8314"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'tiny.png')
    actual = sha256sum_hexdigest(test_file)
    assert actual == e


def test_FileHasher():
    from dtoolcore.filehasher import FileHasher

    def dummy():
        pass

    file_hasher = FileHasher(dummy)
    assert file_hasher.name == "dummy"
