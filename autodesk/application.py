from datetime import datetime


class Application:
    def __init__(self, model, timer, hardware):
        self.model = model
        self.timer = timer
        self.hardware = hardware

    def init(self):
        self.timer.update(datetime.now())
        self.hardware.light(self.model.get_session_state())

    def session_changed(self, event):
        self.hardware.light(event.data)
        self.timer.update(event.index)

    def desk_changed(self, event):
        self.hardware.desk(event.data)
        self.timer.update(event.index)

    def desk_change_disallowed(self, event):
        # TODO: Calculate and schedule next allowed time
        self.timer.cancel()
