try:
    from autodesk.gpio.rpi import OUT, HIGH, LOW, setup, cleanup, output
except:
    try:
        from autodesk.gpio.ft232h import OUT, HIGH, LOW, setup, cleanup, output
    except:
        from autodesk.gpio.print import OUT, HIGH, LOW, setup, cleanup, output
