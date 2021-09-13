import serial

COMPORT = 'COM9'

with serial.Serial(COMPORT, 9600, timeout=2) as ser:

    while True:
        ser.read()
