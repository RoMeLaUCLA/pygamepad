import pygamepad.MemoryManager as MemoryManager
from pyshmxtreme.decorator import WriteSharedMem
import subprocess
import os
import select
import time


# Format floating point number to string format -x.xxx
def fmtFloat(n):
    try:
        return ['{:6.3f}'.format(x) for x in n]
    except TypeError:
        return '{:6.3f}'.format(n)


class Joystick:
    """Initializes the joystick/wireless receiver, launching 'xboxdrv' as a subprocess
    and checking that the wired joystick or wireless receiver is attached.
    The refreshRate determines the maximnum rate at which events are polled from xboxdrv.
    Calling any of the Joystick methods will cause a refresh to occur, if refreshTime has elapsed.
    Routinely call a Joystick method, at least once per second, to avoid overfilling the event buffer.

    Usage:
        joy = pygamepad.Joystick()
    """

    def __init__(self, refreshRate=30):
        self.proc = subprocess.Popen(['xboxdrv', '--no-uinput', '--detach-kernel-driver'], stdout=subprocess.PIPE)
        self.pipe = self.proc.stdout
        #
        self.connectStatus = False  # will be set to True once controller is detected and stays on
        self.reading = '0' * 140  # initialize stick readings to all zeros
        #
        self.refreshTime = 0  # absolute time when next refresh (read results from xboxdrv stdout pipe) is to occur
        self.refreshDelay = 1.0 / refreshRate  # joystick refresh is to be performed 30 times per sec by default
        #
        # Read responses from 'xboxdrv' for upto 2 seconds, looking for controller/receiver to respond
        found = False
        waitTime = time.time() + 2
        while waitTime > time.time() and not found:
            readable, writeable, exception = select.select([self.pipe], [], [], 0)
            if readable:
                response = self.pipe.readline()
                # Hard fail if we see this, so force an error
                if response[0:7] == 'No Xbox':
                    raise IOError('No Xbox controller/receiver found')
                # Success if we see the following
                if response[0:12] == 'Press Ctrl-c':
                    found = True
                # If we see 140 char line, we are seeing valid input
                if len(response) == 140:
                    found = True
                    print('Joystick connected')
                    self.connectStatus = True
                    self.reading = response
        # if the controller wasn't found, then halt
        if not found:
            self.close()
            raise IOError('Unable to detect Xbox controller/receiver - Run python as sudo')

    """Used by all Joystick methods to read the most recent events from xboxdrv.
    The refreshRate determines the maximum frequency with which events are checked.
    If a valid event response is found, then the controller is flagged as 'connected'.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        # self.close()
        pass

    def refresh(self):
        # Refresh the joystick readings based on regular defined freq
        if self.refreshTime < time.time():
            self.refreshTime = time.time() + self.refreshDelay  # set next refresh time
            # If there is text available to read from xboxdrv, then read it.
            readable, writeable, exception = select.select([self.pipe], [], [], 0)
            if readable:
                # Read every line that is availabe.  We only need to decode the last one.
                while readable:
                    response = self.pipe.readline()
                    # A zero length response means controller has been unplugged.
                    if len(response) == 0:
                        raise IOError('Xbox controller disconnected from USB')
                    readable, writeable, exception = select.select([self.pipe], [], [], 0)
                # Valid controller response will be 140 chars.
                if len(response) == 140:
                    self.connectStatus = True
                    self.reading = response
                else:  # Any other response means we have lost wireless or controller battery
                    self.connectStatus = False

    """Return a status of True, when the controller is actively connected.
    Either loss of wireless signal or controller powering off will break connection.  The
    controller inputs will stop updating, so the last readings will remain in effect.  It is
    good practice to only act upon inputs if the controller is connected.  For instance, for
    a robot, stop all motors if "not connected()".

    An inital controller input, stick movement or button press, may be required before the connection
    status goes True.  If a connection is lost, the connection will resume automatically when the
    fault is corrected.
    """

    def connected(self):
        self.refresh()
        return self.connectStatus

    # Left stick X axis value scaled between -1.0 (left) and 1.0 (right) with deadzone tolerance correction
    def leftX(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[3:9])
        return self.axisScale(raw, deadzone)

    # Left stick Y axis value scaled between -1.0 (down) and 1.0 (up)
    def leftY(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[13:19])
        return self.axisScale(raw, deadzone)

    # Right stick X axis value scaled between -1.0 (left) and 1.0 (right)
    def rightX(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[24:30])
        return self.axisScale(raw, deadzone)

    # Right stick Y axis value scaled between -1.0 (down) and 1.0 (up)
    def rightY(self, deadzone=4000):
        self.refresh()
        raw = int(self.reading[34:40])
        return self.axisScale(raw, deadzone)

    # Scale raw (-32768 to +32767) axis with deadzone correcion
    # Deadzone is +/- range of values to consider to be center stick (ie. 0.0)
    def axisScale(self, raw, deadzone):
        if abs(raw) < deadzone:
            return 0.0
        else:
            if raw < 0:
                return (raw + deadzone) / (32768.0 - deadzone)
            else:
                return (raw - deadzone) / (32767.0 - deadzone)

    # Dpad Up status - returns 1 (pressed) or 0 (not pressed)
    def dpadUp(self):
        self.refresh()
        return int(self.reading[45:46])

    # Dpad Down status - returns 1 (pressed) or 0 (not pressed)
    def dpadDown(self):
        self.refresh()
        return int(self.reading[50:51])

    # Dpad Left status - returns 1 (pressed) or 0 (not pressed)
    def dpadLeft(self):
        self.refresh()
        return int(self.reading[55:56])

    # Dpad Right status - returns 1 (pressed) or 0 (not pressed)
    def dpadRight(self):
        self.refresh()
        return int(self.reading[60:61])

    # Back button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='back')
    def Back(self):
        self.refresh()
        return int(self.reading[68:69])

    # Guide button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='guide')
    def Guide(self):
        self.refresh()
        return int(self.reading[76:77])

    # Start button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='start')
    def Start(self):
        self.refresh()
        return int(self.reading[84:85])

    # Left Thumbstick button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='lsb')
    def leftThumbstick(self):
        self.refresh()
        return int(self.reading[90:91])

    # Right Thumbstick button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='rsb')
    def rightThumbstick(self):
        self.refresh()
        return int(self.reading[95:96])

    # A button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='a')
    def A(self):
        self.refresh()
        return int(self.reading[100:101])

    # B button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='b')
    def B(self):
        self.refresh()
        return int(self.reading[104:105])

    # X button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='x')
    def X(self):
        self.refresh()
        return int(self.reading[108:109])

    # Y button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='y')
    def Y(self):
        self.refresh()
        return int(self.reading[112:113])

    # Left Bumper button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='lb')
    def leftBumper(self):
        self.refresh()
        return int(self.reading[118:119])

    # Right Bumper button status - returns 1 (pressed) or 0 (not pressed)
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='rb')
    def rightBumper(self):
        self.refresh()
        return int(self.reading[123:124])

    # Left Trigger value scaled between 0.0 to 1.0
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='lt')
    def leftTrigger(self):
        self.refresh()
        return int(self.reading[129:132]) / 255.0

    # Right trigger value scaled between 0.0 to 1.0
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='rt')
    def rightTrigger(self):
        self.refresh()
        return int(self.reading[136:139]) / 255.0

    # Returns tuple containing X and Y axis values for Left stick scaled between -1.0 to 1.0
    # Usage:
    #     x,y = joy.leftStick()
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='ls')
    def leftStick(self, deadzone=4000):
        self.refresh()
        return self.leftX(deadzone), self.leftY(deadzone)

    # Returns tuple containing X and Y axis values for Right stick scaled between -1.0 to 1.0
    # Usage:
    #     x,y = joy.rightStick()
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='rs')
    def rightStick(self, deadzone=4000):
        self.refresh()
        return self.rightX(deadzone), self.rightY(deadzone)

    # Returns tuple containing dpad up, down, left, and right values
    # Usage:
    #     dup, ddown, dleft, dright = joy.dpad()
    @WriteSharedMem(segment=MemoryManager.DATA_JOYSTICK, block='dpad')
    def dpad(self):
        self.refresh()
        return self.dpadUp(), self.dpadDown(), self.dpadLeft(), self.dpadRight()

    def close(self):
        os.system('pkill xboxdrv')
        print('Joystick disconnected')
    # Cleanup by ending the xboxdrv subprocess


if __name__ == '__main__':
    with Joystick() as joy:

        while True:

            print("connected: ", joy.connected())

            # Left analog stick
            print("Lx,Ly ", fmtFloat(joy.leftStick()))

            # Right analog stick
            print("Rx,Ry ", fmtFloat(joy.rightStick()))

            # Left stick button
            print("Lsb ", fmtFloat(joy.leftThumbstick()))

            # Right stick button
            print("Rsb ", fmtFloat(joy.rightThumbstick()))

            # Left trigger
            print("Ltrg ", fmtFloat(joy.leftTrigger()))

            # Right trigger
            print("Rtrg ", fmtFloat(joy.rightTrigger()))

            # Left bumper
            print("Lbump ", fmtFloat(joy.leftBumper()))

            # Right bumper
            print("Rbump ", fmtFloat(joy.rightBumper()))

            # A/B/X/Y buttons
            print("Buttons "),
            if joy.A():
                print("A"),
            else:
                print(" "),
            if joy.B():
                print("B"),
            else:
                print(" "),
            if joy.X():
                print("X"),
            else:
                print(" "),
            if joy.Y():
                print("Y"),
            else:
                print(" "),

            # Dpad U/D/L/R
            print("Dpad "),
            print(joy.dpad())
