bag2video
=========

Convert images in a rosbag to a variable framerate video. Variable framerate is achieved through duplicating frames since OpenCv can't encode at variable framerates. This can produce very large files which should be re-encoded with something like ffmpeg.

# Usage
    usage: bag2video.py [-h] [--outfile OUTFILE] [--precision PRECISION] [--viz]
                        [--start START] [--end END] [--encoding {rgb8,bgr8,mono8}]
                        topic bagfile
    
    Extract and encode video from bag files.
    
    positional arguments:
      topic
      bagfile
    
    optional arguments:
      -h, --help            show this help message and exit
      --outfile OUTFILE, -o OUTFILE
                            Destination of the video file. Defaults to the
                            location of the input file.
      --precision PRECISION, -p PRECISION
                            Precision of variable framerate interpolation. Higher
                            numbers match the actual framerater better, but result
                            in larger files and slower conversion times.
      --viz, -v             Display frames in a GUI window.
      --start START, -s START
                            Rostime representing where to start in the bag.
      --end END, -e END     Rostime representing where to stop in the bag.
      --encoding {rgb8,bgr8,mono8}
                            Encoding of the deserialized image.
