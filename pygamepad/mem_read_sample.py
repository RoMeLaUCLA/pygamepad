import pygamepad.MemoryManager as MemoryManager
import time

while True:
    data = MemoryManager.DATA_JOYSTICK.get()
    print(data)
    time.sleep(.1)
