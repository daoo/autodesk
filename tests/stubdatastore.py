from autodesk.sqlitedatastore import SqliteDataStore


def empty_data_store(mocker):
    return fake_data_store(mocker, [], [])


def fake_data_store(mocker, session_events, desk_events):
    datastore_fake = mocker.create_autospec(SqliteDataStore, instance=True)
    datastore_fake.get_session_events.return_value = session_events
    datastore_fake.get_desk_events.return_value = desk_events
    datastore_fake.set_session.side_effect = RuntimeError("Not modifiable.")
    datastore_fake.set_desk.side_effect = RuntimeError("Not modifiable.")
    return datastore_fake
