import serial, io, sys, struct


def getWeight(comPort):
    with serial.Serial(comPort,9600,timeout=1) as ser:
        weightReading = ser.read_until(b'\x67')   # read until 'g' appears
        weightReading = float(weightReading.strip(b'\x02\x2b\x20\x67')) #strip SoT, '+', space and 'g'
        return weightReading


if __name__ == "__main__":
    weight = getWeight('COM12')

    print(f"test: the weight on the scale is: {weight}g")        