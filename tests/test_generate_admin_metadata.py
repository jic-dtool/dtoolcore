"""Test the generate_admin_metadata helper function."""

def test_generate_admin_metadata():
    import dtoolcore
    from dtoolcore import generate_admin_metadata
    admin_metadata = generate_admin_metadata("ds-name", "creator-name")
    assert len(admin_metadata["uuid"]) == 36
    assert admin_metadata["dtoolcore_version"] == dtoolcore.__version__
    assert admin_metadata["name"] == "ds-name"
    assert admin_metadata["type"] == "protodataset"
    assert admin_metadata["creator_username"] == "creator-name"
