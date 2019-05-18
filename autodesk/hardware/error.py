class HardwareError(RuntimeError):
    def __init__(self, inner):
        super().__init__(inner)
