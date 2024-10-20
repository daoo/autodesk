import pandas as pd


def empty_data_store(mocker):
    return fake_data_store(mocker, [], [])


def fake_data_store(mocker, session_events, desk_events):
    datastore_fake = mocker.patch(
        "autodesk.sqlitedatastore.SqliteDataStore", autospec=True
    )
    session_events_df = pd.DataFrame(session_events, columns=["timestamp", "state"])
    desk_events_df = pd.DataFrame(desk_events, columns=["timestamp", "state"])
    datastore_fake.get_session_events.return_value = session_events_df
    datastore_fake.get_desk_events.return_value = desk_events_df
    datastore_fake.set_session.side_effect = RuntimeError("Not modifiable.")
    datastore_fake.set_desk.side_effect = RuntimeError("Not modifiable.")
    return datastore_fake
