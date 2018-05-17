from __future__ import print_function
from pygamepad.xbox import Joystick

def fmtFloat(n):
    return '{:6.3f}'.format(n)


class PositionController(object):
    """

    """

    def __init__(self, refresh_rate=30,
                 l_stick_scale_factor = .01,
                 l_trigger_scale_factor = .01,
                 r_stick_scale_factor = .05,
                 r_trigger_scale_factor = .1):

        # Gamepad settings
        self.joy = Joystick(refresh_rate)
        self.refresh_rate = refresh_rate
        self.l_stick_scale_factor = l_stick_scale_factor
        self.l_trigger_scale_factor = l_trigger_scale_factor
        self.r_stick_scale_factor = r_stick_scale_factor
        self.r_trigger_scale_factor = r_trigger_scale_factor
        self.invert_x_axis = False
        self.invert_y_axis = True

        # limits TODO: write settings file that you can import settings from
        self.x_lim = (-.6, .6)
        self.y_lim = (-.6, .6)
        self.z_lim = (0, .6)

        self.roll_lim = (-180, 180)
        self.pitch_lim = (-180, 180)
        self.yaw_lim = (-180, 180)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


    def poll(self,debug=False):

        dp = [0,0,0]
        dr = [0,0,0]

        # Left analog stick control x,y position...
        # FORWARD/BACKWARD is Y axis, LEFT/RIGHT is X axis
        dp[1] = -self.joy.leftX() * self.l_stick_scale_factor
        dp[0] = self.joy.leftY() * self.l_stick_scale_factor

        # left bumper and trigger control z position
        if self.joy.leftBumper():
            dp[2] =  - self.joy.leftTrigger() * self.l_trigger_scale_factor
        else:
            dp[2] = self.joy.leftTrigger() * self.l_trigger_scale_factor

        # Right analog stick controls pitch and yaw
        dr[2] = -self.joy.rightX() * self.r_stick_scale_factor
        dr[1] = self.joy.rightY() * self.r_stick_scale_factor

        # right bumper and trigger control roll
        if self.joy.rightBumper():
            dr[0] = -self.joy.rightTrigger() * self.r_trigger_scale_factor
        else:
            dr[0] = self.joy.rightTrigger() * self.r_trigger_scale_factor

        if debug:
            if self.joy.connected():
                print("Connected   ",)
            else:
                print("Disconnected",)
            print("Lx,Ly ", fmtFloat(dp[0]), fmtFloat(dp[1]), fmtFloat(dp[2]),)
            print("Rx,Ry ", fmtFloat(dr[0]), fmtFloat(dr[1]), fmtFloat(dr[2]),)
            # Move cursor back to start of line
            print(chr(13),)

        return dp, dr, self.joy.A(), self.joy.B(), self.joy.X(), self.joy.Y(), self.joy.Back(), self.joy.connected()

    def close(self):
        self.joy.close()


if __name__ == "__main__":
    print("Xbox controller test: Press Back button to exit")
    # Loop until back button is pressed

    from operator import add


    joy_exit_signal = False

    p = [0,0,0]
    r = [0,0,0]
    JC = PositionController(refresh_rate=30)
    try:
        while not joy_exit_signal:
            print(JC.poll(debug=False))
            dp, dr, a_pressed, b_pressed, x_pressed, y_pressed, joy_exit_signal, joy_connected = JC.poll(debug=False)
            print("dp: {} dr: {}".format(dp,dr))
            print(chr(13))

    finally:
        # Close out when done
        JC.close()
