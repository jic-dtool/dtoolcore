"""Test timestamp functionality."""

from datetime import datetime


def test_timestamp_returns_float():
    import dtoolcore.utils

    start_of_time = datetime(1970, 1, 1)

    assert type(dtoolcore.utils.timestamp(start_of_time)) is float


def test_start_of_time_is_0():
    import dtoolcore.utils

    start_of_time = datetime(1970, 1, 1)

    assert dtoolcore.utils.timestamp(start_of_time) == 0.0


def test_millenium_is_946684800():

    import dtoolcore.utils

    start_of_time = datetime(2000, 1, 1)

    assert dtoolcore.utils.timestamp(start_of_time) == 946684800.


def test_subsection_precision():

    import dtoolcore.utils

    time_as_float = 946684800.513
    into_new_millenium = datetime.fromtimestamp(time_as_float)

    tolerance = 0.000001
    actual = dtoolcore.utils.timestamp(into_new_millenium)
    assert actual < time_as_float + tolerance
    assert actual > time_as_float - tolerance
