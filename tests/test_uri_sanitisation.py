
import os


def test_generous_parse_uri():

    from dtoolcore.utils import generous_parse_uri

    s3_uri = "s3://my-bucket/path/to/files"

    parse_result = generous_parse_uri(s3_uri)

    assert parse_result.scheme == 's3'
    assert parse_result.netloc == 'my-bucket'
    assert parse_result.path == '/path/to/files'


    lazy_file_uri = ".my_dataset"

    parse_result = generous_parse_uri(lazy_file_uri)
    assert parse_result.scheme == 'file'

    full_file_uri = "file://localhost/path/to/files"
    parse_result = generous_parse_uri(full_file_uri)

    assert parse_result.scheme == 'file'
    assert parse_result.netloc == 'localhost'
    assert parse_result.path == '/path/to/files'

    irods_uri = "irods:///jic_raw_data/rg-someone/my_dataset"
    parse_result = generous_parse_uri(irods_uri)

    assert parse_result.scheme == 'irods'
    assert parse_result.netloc == ''
    assert parse_result.path == '/jic_raw_data/rg-someone/my_dataset'

    irods_uri = "irods:/jic_raw_data/rg-someone/my_dataset"
    parse_result = generous_parse_uri(irods_uri)

    assert parse_result.scheme == 'irods'
    assert parse_result.netloc == ''
    assert parse_result.path == '/jic_raw_data/rg-someone/my_dataset'


def test_sanitise_uri():

    from dtoolcore.utils import sanitise_uri

    relpath = "./my_data"

    abspath = os.path.abspath(relpath)

    sanitised_uri = sanitise_uri(relpath)
    expected_uri = "file://localhost{}".format(abspath)
    assert sanitised_uri == expected_uri


    s3_uri = "s3://my-bucket/path/to/files"
    sanitised_uri = sanitise_uri(s3_uri)
    assert sanitised_uri == s3_uri

    irods_uri = "irods:///jic_raw_data/rg-someone/my_dataset"
    sanitised_uri = sanitise_uri(irods_uri)
    expected_uri = "irods:/jic_raw_data/rg-someone/my_dataset"
    assert sanitised_uri == expected_uri
