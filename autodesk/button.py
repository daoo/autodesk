class Button:
    def __init__(self, pin, autodeskservice):
        self.pin = pin
        self.autodeskservice = autodeskservice
        self.buttondown = False

    def poll(self):
        value = self.pin.read()
        if value == 1 and not self.buttondown:
            self.autodeskservice.toggle_session()
            self.buttondown = True
        elif value == 0:
            self.buttondown = False
