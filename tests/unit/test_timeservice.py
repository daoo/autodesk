from datetime import datetime

from autodesk.application.timeservice import UTC, TimeService


def test_timeservice_min_is_utc():
    service = TimeService()
    assert service.min.tzinfo == UTC
    assert service.min == datetime(1970, 1, 1, tzinfo=UTC)


def test_timeservice_now_is_utc():
    service = TimeService()
    now = service.now()
    assert isinstance(now, datetime)
    assert now.tzinfo == UTC
