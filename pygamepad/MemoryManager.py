import pyshmxtreme as shmx
import numpy as np

# gamepad data
DATA_JOYSTICK = shmx.SHMSegment(robot_name='PEBLE', seg_name='JOYSTICK')
DATA_JOYSTICK.add_blocks(name='ls', data=np.zeros(2))  # left stick
DATA_JOYSTICK.add_blocks(name='rs', data=np.zeros(2))  # right stick
DATA_JOYSTICK.add_blocks(name='lsb', data=np.zeros(1))  # left stick button
DATA_JOYSTICK.add_blocks(name='rsb', data=np.zeros(1))  # right stick button
DATA_JOYSTICK.add_blocks(name='dpad', data=np.zeros(4))  # directional pad
DATA_JOYSTICK.add_blocks(name='back', data=np.zeros(1))
DATA_JOYSTICK.add_blocks(name='guide', data=np.zeros(1))
DATA_JOYSTICK.add_blocks(name='start', data=np.zeros(1))
DATA_JOYSTICK.add_blocks(name='a', data=np.zeros(1))
DATA_JOYSTICK.add_blocks(name='b', data=np.zeros(1))
DATA_JOYSTICK.add_blocks(name='x', data=np.zeros(1))
DATA_JOYSTICK.add_blocks(name='y', data=np.zeros(1))
DATA_JOYSTICK.add_blocks(name='lb', data=np.zeros(1))  # left bumper
DATA_JOYSTICK.add_blocks(name='rb', data=np.zeros(1))  # right bumper
DATA_JOYSTICK.add_blocks(name='lt', data=np.zeros(1))  # left trigger
DATA_JOYSTICK.add_blocks(name='rt', data=np.zeros(1))  # right trigger


def init():
    DATA_JOYSTICK.initialize = True


def connect():
    DATA_JOYSTICK.connect_segment()


if __name__ == '__main__':
    init()
    connect()
else:
    connect()
