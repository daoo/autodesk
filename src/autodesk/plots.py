import base64
from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def _figure_to_base64(figure: Figure) -> str:
    tmpfile = BytesIO()
    metadata = {"Software": "AutoDesk https://github.com/daoo/autodesk"}
    figure.savefig(tmpfile, format="png", metadata=metadata)
    return base64.b64encode(tmpfile.getvalue()).decode("utf-8")


def _plot_weekday_hourly_count(full_week: pd.DataFrame, dpi: int = 80) -> Figure:
    working_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    filtered = full_week[
        (full_week.weekday.isin(working_days))
        & (full_week.hour >= 6)
        & (full_week.hour <= 20)
    ]
    counts = filtered["counts"]
    relative = (counts - counts.min()) / (counts.max() - counts.min())

    figure = plt.figure(figsize=(800 / dpi, 400 / dpi), dpi=dpi)
    figure.suptitle("Weekday Hourly Relative Presence")
    ax = figure.add_subplot()
    ax.set_xlabel("Hour")
    ax.scatter(
        x=filtered.hour,
        y=filtered.weekday.index,
        s=relative * 500,
        color="grey",
    )
    ax.set_yticks(range(len(working_days)), working_days)
    return figure


def plot_weekday_hourly_count_png(
    full_week: pd.DataFrame, png_path: str, dpi: int = 80
) -> None:
    figure = _plot_weekday_hourly_count(full_week, dpi=dpi)
    try:
        figure.savefig(png_path, format="png")
    finally:
        plt.close(figure)


def plot_weekday_hourly_count_base64(full_week: pd.DataFrame, dpi: int = 80) -> str:
    figure = _plot_weekday_hourly_count(full_week, dpi=dpi)
    try:
        data = _figure_to_base64(figure)
    finally:
        plt.close(figure)
    return data
