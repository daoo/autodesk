from autodesk.spans import Event
from datetime import datetime, timedelta
import logging


class Application:
    def __init__(self, model, timer, hardware, limits):
        self.logger = logging.getLogger('application')
        self.model = model
        self.timer = timer
        self.hardware = hardware
        self.limits = limits

    def init(self):
        self.hardware.light(self.model.get_session_state())
        self._update_timer(
            datetime.now(),
            self.model.get_desk_state(),
            self.model.get_session_state())

    def session_changed(self, event):
        self.hardware.light(event.data)
        self._update_timer(event.index, self.model.get_desk_state(), event.data)

    def desk_changed(self, event):
        self.hardware.desk(event.data)
        self._update_timer(event.index, event.data, self.model.get_session_state())

    def desk_change_disallowed(self, event):
        # TODO: Calculate and schedule next allowed time
        self.timer.cancel()

    def _update_timer(self, time, desk, session):
        if not session.active():
            self.logger.info('session is inactive, not scheduling')
            self.timer.cancel()
            return

        active_time = self.model.get_active_time(datetime.min, time)
        limit = desk.test(*self.limits)
        delay = max(timedelta(0), limit - active_time)
        event = Event(datetime.now(), desk.next())
        self.timer.schedule(delay, lambda: self.model.set_desk(event))
