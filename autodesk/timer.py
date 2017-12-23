from datetime import datetime, timedelta
import autodesk.stats as stats


class Communicator:
    def __init__(self, path):
        self.path = path

    def schedule(self, delay, target):
        assert delay >= timedelta(0)
        with open(self.path, 'w') as timer_file:
            seconds = int(delay.total_seconds())
            timer_file.write(str(seconds) + ' ' + target.test('0', '1') + '\n')

    def cancel(self):
        with open(self.path, 'w') as timer_file:
            timer_file.write('cancel\n')


class Timer:
    def __init__(self, limits, communicator, database):
        self.communicator = communicator
        self.limits = limits
        self.database = database

    def session_changed(self, time, state):
        self.update(time)

    def desk_changed(self, time, state):
        self.update(time)

    def desk_change_disallowed(self, time):
        # TODO: Calculate and schedule next allowed time
        self.communicator.cancel()

    def update(self, time):
        beginning = datetime.fromtimestamp(0)
        session_spans = self.database.get_session_spans(beginning, time)
        if not session_spans[-1].data.active():
            self.communicator.cancel()
            return

        desk_spans = self.database.get_desk_spans(beginning, time)
        desk = desk_spans[-1].data
        active_time = stats.compute_active_time(session_spans, desk_spans)
        limit = desk.test(*self.limits)
        delay = max(timedelta(0), limit - active_time)
        self.communicator.schedule(delay, desk.next())
