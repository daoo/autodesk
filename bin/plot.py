from autodesk.model import Model
from autodesk.plots import plot_weekday_hourly_count
from autodesk.sqlitedatastore import SqliteDataStore
from pandas import Timestamp
import sys

model = Model(SqliteDataStore(sys.argv[1]))
figure = plot_weekday_hourly_count(
    model.compute_hourly_count(
        Timestamp.min,
        Timestamp.now()
    ))
figure.savefig(sys.argv[2], format='png')
