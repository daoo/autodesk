import asyncio


POLLING_DELAY = 0.1


class Button:
    def __init__(self, pin, autodeskservice):
        self.pin = pin
        self.autodeskservice = autodeskservice

    async def poll(self):
        buttondown = False
        while True:
            value = self.pin.read()
            if value == 1 and not buttondown:
                self.autodeskservice.toggle_session()
                buttondown = True
            elif value == 0:
                buttondown = False
            await asyncio.sleep(POLLING_DELAY)
