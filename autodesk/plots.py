import matplotlib.pyplot as plt


def plot_weekday_relative_frequency(frequency, dpi=80):
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    filtered = frequency[weekdays]
    filtered = filtered[(frequency.index >= 8) & (frequency.index <= 18)]

    fig = plt.figure(figsize=(800 / dpi, 400 / dpi), dpi=dpi)
    fig.suptitle('Weekday Frequency')
    ax = fig.add_subplot(111)
    ax.set(xlabel='Hour', ylabel='Frequency')
    filtered.plot(ax=ax, kind='bar')
    return fig
