from datetime import timedelta


class Timer:
    def __init__(self, path):
        self.path = path

    def schedule(self, delay, target):
        assert delay >= timedelta(0)
        with open(self.path, 'w') as timer_file:
            seconds = int(delay.total_seconds())
            timer_file.write(str(seconds) + ' ' + target.test('0', '1') + '\n')

    def stop(self):
        with open(self.path, 'w') as timer_file:
            timer_file.write('stop\n')
