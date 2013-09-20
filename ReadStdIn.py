import argparse
import sys

desc='Generate noisy dot field trial set'
help_format=argparse.ArgumentDefaultsHelpFormatter
parser = argparse.ArgumentParser(description=desc,\
                                 formatter_class=help_format)

# trial parameters
parser.add_argument('-n','--n-dirs',default=8,type=int,\
                        choices=range(0,360),metavar='N_DIRS',\
                        help='set number of directions')
parser.add_argument('-b','--base-angle',default=0,type=int,
                        choices=range(0,360),metavar='BASE_ANGLE',\
                        help='set the base angle; '+\
                        'full direction set is the set of N_DIRS evenly '+\
                        'distributed around the circle that includes '+\
                        'BASE_ANGLE')
parser.add_argument('-d','--field-size',nargs=2,\
                        metavar=('width(deg)','height (cm)'),\
                        default=[40,40],type=int,choices=range(0,50),\
                        help='set trial screen size (deg)')
parser.add_argument('-s','--speed',type=float,default=20.0,\
                        help='set the target speed')

# perturbation parameters
parser.add_argument('-p','--pert-gain',type=float,default=0.0,\
                        nargs='+',help='set the perturbation gain(s)')
parser.add_argument('--n-dots',type=int,default=350,\
                        help='set the number of dots')
parser.add_argument('--filter-cut-off',type=float,default=32,\
                        help='set the cut off frequency of the filter')
parser.add_argument('--segment-duration',nargs='+',default=500,\
                        type=int,choices=range(0,9999),\
                        metavar='SEGMENT_DURATION',\
                        help='set segment durations; if multiple values '+\
                        'are given, they are assigned in order to the '+\
                        'perturbation segments, if one value is given it '+\
                        'is assigned to all segments')

# screen parameters
parser.add_argument('--resolution',type=int,nargs=2,default=[1024,768],\
                        metavar=('width (deg)','height (deg)'),\
                        help='set the display width and height in pixels')
parser.add_argument('--screen-size',type=float,nargs=2,default=[32.0,29.1],\
                        metavar=('width (cm)','height (cm)'),\
                        help='set the display width and height in cm')
parser.add_argument('--refresh-rate',type=int,default=85,\
                        help='set the monitor refresh rate')
parser.add_argument('--dist-to-eye',type=float,default=48.5,\
                        help='set the distance to eye in cm')

parser.add_argument('-v','--verbose',action='store_true',help='be verbose')

xor=lambda A, B : ((not A) and B) or (A and (not B)) 

def parse(stdin):
    if xor('--resolution' in stdin,'--screen-size' in stdin):
        error_msg='Specify both or neither --resolution and '+\
                    '--screen-size'
        raise ValueError(error_msg)
    args = parser.parse_args(stdin)
    return args

if __name__ == '__main__':
    parse(sys.argv[1:])
