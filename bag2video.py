#!/usr/bin/env python

from __future__ import division
import rosbag, rospy, numpy as np
import sys, os, cv2, glob
from cv_bridge import CvBridge
from itertools import izip, repeat
import argparse

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

def write_frames(bag, writer, total, topic=None, nframes=repeat(1), start_time=rospy.Time(0), stop_time=rospy.Time(sys.maxint), viz=False, encoding='bgr8'):
    bridge = CvBridge()
    if viz:
        cv2.namedWindow('win')
    count = 1
    iterator = bag.read_messages(topics=topic, start_time=start_time, end_time=stop_time)
    for (topic, msg, time), reps in izip(iterator, nframes):
        print '\rWriting frame %s of %s at time %s' % (count, total, time),
        img = np.asarray(bridge.imgmsg_to_cv(msg, 'bgr8'))
        for rep in range(reps):
            writer.write(img)
        imshow('win', img)
        count += 1

def imshow(win, img):
    cv2.imshow(win, img)
    cv2.waitKey(1)

def noshow(win, img):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and encode video from bag files.')
    parser.add_argument('--outfile', '-o', action='store', default=None,
                        help='Destination of the video file. Defaults to the location of the input file.')
    parser.add_argument('--precision', '-p', action='store', default=10, type=int,
                        help='Precision of variable framerate interpolation. Higher numbers\
                        match the actual framerater better, but result in larger files and slower conversion times.')
    parser.add_argument('--viz', '-v', action='store_true', help='Display frames in a GUI window.')
    parser.add_argument('--start', '-s', action='store', default=rospy.Time(0), type=rospy.Time,
                        help='Rostime representing where to start in the bag.')
    parser.add_argument('--end', '-e', action='store', default=rospy.Time(sys.maxint), type=rospy.Time,
                        help='Rostime representing where to stop in the bag.')
    parser.add_argument('--encoding', choices=('rgb8', 'bgr8', 'mono8'), default='bgr8',
                        help='Encoding of the deserialized image.')

    parser.add_argument('topic')
    parser.add_argument('bagfile')

    args = parser.parse_args()

    if not args.viz:
        imshow = noshow

    for bagfile in glob.glob(args.bagfile):
        print bagfile
        outfile = args.outfile
        if not outfile:
            outfile = os.path.join(*os.path.split(bagfile)[-1].split('.')[:-1]) + '.avi'
        bag = rosbag.Bag(bagfile, 'r')
        print 'Calculating video properties'
        rate, minrate, maxrate, size, times = get_info(bag, args.topic, start_time=args.start, stop_time=args.end)
        nframes = calc_n_frames(times, args.precision)
        # writer = cv2.VideoWriter(outfile, cv2.cv.CV_FOURCC(*'DIVX'), rate, size)
        writer = cv2.VideoWriter(outfile, cv2.cv.CV_FOURCC(*'DIVX'), np.ceil(maxrate*args.precision), size)
        print 'Writing video'
        write_frames(bag, writer, len(times), topic=args.topic, nframes=nframes, start_time=args.start, stop_time=args.end, encoding=args.encoding)
        writer.release()
        print '\n'
