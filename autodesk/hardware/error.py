class HardwareError(RuntimeError):
    def __init__(self, inner):
        super(RuntimeError, self).__init__(inner)
