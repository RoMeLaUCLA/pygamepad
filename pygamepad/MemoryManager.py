import pyshmxtreme.SHMSegment as shmx
import numpy as np

CONTROLLER_MEM = shmx.SHMSegment(robot_name='PEBLE', seg_name='xbox')
CONTROLLER_MEM.add_blocks(name='ls', data=np.zeros(2,))
CONTROLLER_MEM.add_blocks(name='rs', data=np.zeros(2,))
CONTROLLER_MEM.add_blocks(name='lsb', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='rsb', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='dpad', data=np.zeros(4,))
CONTROLLER_MEM.add_blocks(name='back', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='guide', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='start', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='a', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='b', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='x', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='y', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='lb', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='rb', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='lt', data=np.zeros(1,))
CONTROLLER_MEM.add_blocks(name='rt', data=np.zeros(1,))


def init():
    CONTROLLER_MEM.initialize = True


def connect():
    CONTROLLER_MEM.connect_segment()


if __name__ == '__main__':
    init()
    connect()
else:
    connect()
