"""Test the generate_admin_metadata helper function."""

import datetime
import pytz


def test_generate_admin_metadata():
    import dtoolcore
    from dtoolcore import generate_admin_metadata
    admin_metadata = generate_admin_metadata("ds-name", "creator-name")
    assert len(admin_metadata["uuid"]) == 36
    assert admin_metadata["dtoolcore_version"] == dtoolcore.__version__
    assert admin_metadata["name"] == "ds-name"
    assert admin_metadata["type"] == "protodataset"
    assert admin_metadata["creator_username"] == "creator-name"

    assert type(admin_metadata["created_at"]) is float

    time_from_admin_metadata = datetime.datetime.fromtimestamp(
        float(admin_metadata['created_at']),
        tz=pytz.UTC
    )
    time_delta = datetime.datetime.now(tz=pytz.UTC) - time_from_admin_metadata
    assert time_delta.days == 0
    assert time_delta.seconds < 20
