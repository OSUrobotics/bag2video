#!/usr/bin/env python

from __future__ import division
import rosbag, rospy, numpy as np
import sys, os, cv2
from cv_bridge import CvBridge
from itertools import izip, repeat
PRECISION = 10

def get_info(bag, topic=None, start_time=rospy.Time(0), stop_time=rospy.Time(sys.maxint)):
    size = (0,0)
    times = []

    # read the first message to get the image size
    msg = bag.read_messages(topics=topic).next()[1]
    size = (msg.width, msg.height)

    # now read the rest of the messages for the rates
    iterator = bag.read_messages(topics=topic, start_time=start_time, end_time=stop_time)#, raw=True)
    for _, msg, _ in iterator:
        time = msg.header.stamp
        times.append(time.to_sec())
        size = (msg.width, msg.height)
    diffs = 1/np.diff(times)
    return np.median(diffs), min(diffs), max(diffs), size, times

def calc_n_frames(times, precision=10):
    # the smallest interval should be one frame, larger intervals more
    intervals = np.diff(times)
    return np.int64(np.round(precision*intervals/min(intervals)))

def write_frames(bag, writer, topic=None, nframes=repeat(1), start_time=rospy.Time(0), stop_time=rospy.Time(sys.maxint)):
    bridge = CvBridge()
    cv2.namedWindow('win')
    iterator = bag.read_messages(topics=topic, start_time=start_time, end_time=stop_time)
    for (topic, msg, time), reps in izip(iterator, nframes):
        print 'Writing frame at time ', time
        img = np.asarray(bridge.imgmsg_to_cv(msg, 'rgb8'))
        for rep in range(reps):
            writer.write(img)
        cv2.imshow('win', img)
        cv2.waitKey(1)

if __name__ == '__main__':
    filename = '/mnt/hgfs/lazewatd/2013-08-22-16-18-36.bag'
    outfile = os.path.join(*os.path.split(filename)[-1].split('.')[:-1]) + '.avi'
    # rate = 13
    # size = (640, 480)
    bag = rosbag.Bag(filename, 'r')
    print 'Calculating video properties'
    rate, minrate, maxrate, size, times = get_info(bag, '/head_mount_kinect/rgb/image_raw', stop_time=rospy.Time(1377213524600930397))
    nframes = calc_n_frames(times, PRECISION)
    # writer = cv2.VideoWriter(outfile, cv2.cv.CV_FOURCC(*'DIVX'), rate, size)
    writer = cv2.VideoWriter(outfile, cv2.cv.CV_FOURCC(*'DIVX'), np.ceil(maxrate*PRECISION), size)
    print 'Writing video'
    write_frames(bag, writer, '/head_mount_kinect/rgb/image_raw', nframes, stop_time=rospy.Time(1377213524600930000))
    writer.release()