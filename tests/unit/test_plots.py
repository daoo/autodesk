from autodesk.plots import (
    plot_weekday_hourly_count_base64,
    plot_weekday_hourly_count_png,
)

FULL_WEEK = [
    ("Monday", 8, 1),
    ("Monday", 9, 2),
    ("Tuesday", 10, 0),
    ("Friday", 20, 3),
]


def test_plot_png_creates_file(tmp_path):
    png_path = tmp_path / "figure.png"
    plot_weekday_hourly_count_png(FULL_WEEK, str(png_path))
    assert png_path.exists()
    assert png_path.stat().st_size > 0


def test_plot_base64_returns_string():
    data = plot_weekday_hourly_count_base64(FULL_WEEK)
    assert isinstance(data, str)
    assert len(data) > 0
