import argparse
import sys
import time
import textwrap

print_date='noisy_field-'+time.strftime('%Y:%m:%d:%H:%M:%S')
wrap=lambda s : textwrap.fill(s,80)
with open('MakeTrial.readme') as f:
    l=f.readlines()
    s=map(wrap,l)
    desc='\n'.join(s).strip('\n')

# Combine RawText and ArgumentDefaults help formatters and line wrap pre-print
class CustomHelpFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])
    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help
parser = argparse.ArgumentParser(description=desc,
                                 formatter_class=CustomHelpFormatter,
                                 fromfile_prefix_chars='@')

# trial parameters
trial_opt=parser.add_argument_group('Trial Parameters')
trial_opt.add_argument('--trial-name',type=str,default=print_date,
                        metavar='trialname::str',help='set the trial name')
#trial_opt.add_argument('--n-dirs',default=8,type=int,
#                        choices=range(0,360),metavar='n_dirs::int',
#                        help='set number of directions')
#trial_opt.add_argument('--base-angle',default=0,type=int,
#                        choices=range(0,360),metavar='base_angle::degrees',
#                        help='set the base angle; '+\
#                        'full direction set is the set of N_DIRS evenly '+\
#                        'distributed around the circle that includes '+\
#                        'BASE_ANGLE')
trial_opt.add_argument('--angle',type=float,nargs='+',default=[0.0],
                        metavar='direction::degrees',
                        help='set the direction of each segment')
trial_opt.add_argument('--angle-var',type=float,nargs='+',default=[0.0],
                        metavar='sigma::degrees',
                        help='set the target direction variance')
trial_opt.add_argument('--field-size',metavar='radius::deg',
                        default=40.0,type=float,
                        help='set trial display dimensions')
trial_opt.add_argument('--field-center',nargs=2,
                        metavar=('x_pos::deg','y_pos::deg'),
                        default=[0.0,0.0],type=float,
                        help='set trial display center')
trial_opt.add_argument('--speed',type=float,nargs='+',default=[20.0],
                        metavar='speed::deg/s',help='set the mean target speed')
trial_opt.add_argument('--speed-var',type=float,nargs='+',default=[0.0],
                        metavar='sigma::deg/s',
                        help='set the target speed variance')
trial_opt.add_argument('--window-speed',type=float,nargs='+',default=[0.0],
                        metavar='speed::deg/s',
                        help='set window speed')
trial_opt.add_argument('--fix-dur',type=int,default=85,
                        metavar='duration::frames',
                        help='set the duration of pre and post fixation')

# perturbation parameters
pert_opt=parser.add_argument_group('Perturbation Parameters')
pert_opt.add_argument('--noise-update',type=int,default=10,
						metavar='n::frames',
						help='set the noise update interval (frames)')
pert_opt.add_argument('--pert-gain',type=float,default=[0.0],
                        metavar='sigma::deg',
                        nargs='+',help='set the perturbation variance(s); '+\
                        'determines the number of unique perturbation segments')
pert_opt.add_argument('--pert-var',type=float,default=[0.0],
                        metavar='sigma::deg',nargs='+',
                        help='set the variance of the perturbation hyper '+\
                        'distribution')
pert_opt.add_argument('--repeat',type=int,default=1,metavar='repeat::int',
                        help='set the number of times to repeat the '+\
                        'perturbation pattern')
pert_opt.add_argument('--dot-density',type=float,default=4,
                        metavar='density::dots/deg**2',
                        help='set the number of dots')
pert_opt.add_argument('--dot-size',metavar=('width::deg','height::deg'),
                        type=float,default=[0.25,0.25],nargs=2,
                        help='set the dot size')
pert_opt.add_argument('--filter-cut-off',type=float,default=32,
                        metavar='frequncy::Hz',
                        help='set the cut off frequency of the filter')
pert_opt.add_argument('--segment-duration',nargs='+',default=[85],
                        type=int,metavar='duration::frames',
                        help='set segment durations in units of frames; '+\
                        'if multiple values '+\
                        'are given, they are assigned in order to the '+\
                        'perturbation segments, if one value is given it '+\
                        'is assigned to all segments')

# screen parameters
screen_opt=parser.add_argument_group('Screen Parameters')
screen_opt.add_argument('--resolution',type=int,nargs=2,default=[1024,768],
                        metavar=('width::deg','height::deg'),
                        help='set the display width and height in pixels')
screen_opt.add_argument('--screen-size',type=float,nargs=2,default=[32.0,29.1],
                        metavar=('width::cm','height::cm'),
                        help='set the display width and height in cm')
screen_opt.add_argument('--refresh-rate',type=int,default=85,
                        metavar='REFRESH_RATE::Hz',
                        help='set the monitor refresh rate')
screen_opt.add_argument('--dist-to-eye',type=float,default=48.5,
                        metavar='DIST_TO_EYE::cm',
                        help='set the distance to eye in cm')

depr=parser.add_argument_group('Deprecated')
depr.add_argument('--pert-mean',type=float,default=[0.0],
                        metavar='mu::deg',nargs='+',
                        help='set the mean of the perturbation hyper '+\
                        'distribution')

# General
parser.add_argument('-v','--verbose',type=int,default=1,
                    choices=[0,1,2,3],
                    help='set verbosity level. 0 prints nothing whatsoever, '+\
                        '1 prints basic progress, 2 prints commands, '+\
                        '3 prints all avconv output')
parser.add_argument('--save-path',type=str,default='trials',
                    help='set the trial save path')

xor=lambda A, B : ((not A) and B) or (A and (not B)) 

## Overwrite file argument converter
def convert_arg_line_to_args(arg_line):
    for arg in arg_line.split():
        if not arg.strip():
            continue
        yield arg

parser.convert_arg_line_to_args = convert_arg_line_to_args

def parse(stdin):
    if xor('--resolution' in stdin,'--screen-size' in stdin):
        error_msg='Specify both or neither --resolution and '+\
                    '--screen-size'
        raise ValueError(error_msg)
    args = parser.parse_args(stdin)
    return vars(args)

if __name__ == '__main__':
    parse(sys.argv[1:])
