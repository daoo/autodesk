from io import BytesIO
import base64
import matplotlib.pyplot as plt


def figure_to_base64(figure):
    tmpfile = BytesIO()
    figure.savefig(tmpfile, format='png')
    return base64.b64encode(tmpfile.getvalue()).decode('utf-8')


def plot_weekday_relative_frequency(frequency, dpi=80):
    working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    filtered = frequency[
        (frequency.weekday.isin(working_days)) &
        (frequency.hour >= 8) & (frequency.hour <= 18)
    ]

    figure = plt.figure(figsize=(800 / dpi, 400 / dpi), dpi=dpi)
    figure.suptitle('Weekday Frequency')
    ax = figure.add_subplot(111)
    ax.set(xlabel='Hour')
    ax.scatter(
        x=filtered.hour,
        y=filtered.weekday,
        s=filtered.frequency * 100,
        color='grey')
    return figure
