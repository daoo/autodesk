import base64
from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from autodesk.model import HourlyCount


def _figure_to_base64(figure: Figure) -> str:
    tmpfile = BytesIO()
    metadata = {"Software": "AutoDesk https://github.com/daoo/autodesk"}
    figure.savefig(tmpfile, format="png", metadata=metadata)
    return base64.b64encode(tmpfile.getvalue()).decode("utf-8")


def _plot_weekday_hourly_count(full_week: list[HourlyCount], dpi: int = 80) -> Figure:
    working_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    filtered = [
        row
        for row in full_week
        if row[0] in working_days and row[1] >= 6 and row[1] <= 20
    ]
    counts = [row[2] for row in filtered]
    minimum = min(counts) if counts else 0
    maximum = max(counts) if counts else 0
    span = maximum - minimum
    relative = [0 if span == 0 else (count - minimum) / span for count in counts]

    figure = plt.figure(figsize=(800 / dpi, 400 / dpi), dpi=dpi)
    figure.suptitle("Weekday Hourly Relative Presence")
    ax = figure.add_subplot()
    ax.set_xlabel("Hour")
    weekday_index = {day: idx for idx, day in enumerate(working_days)}
    ax.scatter(
        x=[row[1] for row in filtered],
        y=[weekday_index[row[0]] for row in filtered],
        s=[size * 500 for size in relative],
        color="grey",
    )
    ax.set_yticks(range(len(working_days)), working_days)
    return figure


def plot_weekday_hourly_count_png(
    full_week: list[HourlyCount],
    png_path: str,
    dpi: int = 80,
) -> None:
    figure = _plot_weekday_hourly_count(full_week, dpi=dpi)
    try:
        figure.savefig(png_path, format="png")
    finally:
        plt.close(figure)


def plot_weekday_hourly_count_base64(
    full_week: list[HourlyCount],
    dpi: int = 80,
) -> str:
    figure = _plot_weekday_hourly_count(full_week, dpi=dpi)
    try:
        data = _figure_to_base64(figure)
    finally:
        plt.close(figure)
    return data
