import sys

from pandas import Timestamp

from autodesk.model import Model
from autodesk.plots import plot_weekday_hourly_count_png
from autodesk.sqlitedatastore import SqliteDataStore

model = Model(SqliteDataStore.open(sys.argv[1]))
figure = plot_weekday_hourly_count_png(
    model.compute_hourly_count(Timestamp.min, Timestamp.now()),
    png_path=sys.argv[2],
)
