from datetime import datetime

from autodesk.sqlitedatastore import SqliteDataStore


def empty_data_store(mocker):
    return fake_data_store(mocker, [], [])


def fake_data_store(mocker, session_events, desk_events):
    def last_event(events):
        return events[-1] if events else None

    def last_event_before(events, at: datetime):
        candidates = [event for event in events if event[0] <= at]
        return candidates[-1] if candidates else None

    def events_between(events, initial: datetime, final: datetime):
        return [event for event in events if initial <= event[0] <= final]

    datastore_fake = mocker.create_autospec(SqliteDataStore, instance=True)
    datastore_fake.get_last_session_event.return_value = last_event(session_events)
    datastore_fake.get_last_desk_event.return_value = last_event(desk_events)
    datastore_fake.get_last_session_event_before.side_effect = (
        lambda at: last_event_before(session_events, at)
    )
    datastore_fake.get_last_desk_event_before.side_effect = (
        lambda at: last_event_before(desk_events, at)
    )
    datastore_fake.get_session_events_between.side_effect = (
        lambda initial, final: events_between(session_events, initial, final)
    )
    datastore_fake.get_desk_events_between.side_effect = (
        lambda initial, final: events_between(desk_events, initial, final)
    )
    datastore_fake.set_session.side_effect = RuntimeError("Not modifiable.")
    datastore_fake.set_desk.side_effect = RuntimeError("Not modifiable.")
    return datastore_fake
