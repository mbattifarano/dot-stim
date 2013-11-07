from defaults import TrialParameters
import time
import textwrap
import argparse

wrap=lambda s : textwrap.fill(s,80)
with open('MakeTrial.readme') as f:
    l=f.readlines()
    s=map(wrap,l)
    desc='\n'.join(s).strip('\n')

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
trial_opt.add_argument('--trial-name',type=str,default=TrialParameters.trial_name,
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
trial_opt.add_argument('--angle',type=float,nargs='+',default=TrialParameters.angle,
                        metavar='direction::degrees',
                        help='set the direction of each segment')
trial_opt.add_argument('--angle-var',type=float,nargs='+',default=TrialParameters.angle_var,
                        metavar='sigma::degrees',
                        help='set the target direction variance')
trial_opt.add_argument('--field-size',metavar='radius::deg',
                        default=TrialParameters.field_size,type=float,
                        help='set trial display dimensions')
trial_opt.add_argument('--field-center',nargs=2,
                        metavar=('x_pos::deg','y_pos::deg'),
                        default=TrialParameters.field_center,type=float,
                        help='set trial display center')
trial_opt.add_argument('--speed',type=float,nargs='+',default=TrialParameters.speed,
                        metavar='speed::deg/s',help='set the mean target speed')
trial_opt.add_argument('--speed-var',type=float,nargs='+',default=TrialParameters.speed_var,
                        metavar='sigma::deg/s',
                        help='set the target speed variance')
trial_opt.add_argument('--window-speed',type=float,nargs='+',default=TrialParameters.window_speed,
                        metavar='speed::deg/s',
                        help='set window speed')
trial_opt.add_argument('--fix-dur',type=int,default=TrialParameters.fix_dur,
                        metavar='duration::frames',
                        help='set the duration of pre and post fixation')
trial_opt.add_argument('--end-jump',action='store_true')

# perturbation parameters
pert_opt=parser.add_argument_group('Perturbation Parameters')
pert_opt.add_argument('--pert-gain',type=float,default=TrialParameters.pert_gain,
                        metavar='sigma::deg',
                        nargs='+',help='set the perturbation variance(s); '+\
                        'determines the number of unique perturbation segments')
pert_opt.add_argument('--pert-var',type=float,default=TrialParameters.pert_var,
                        metavar='sigma::deg',nargs='+',
                        help='set the variance of the perturbation hyper '+\
                        'distribution')
pert_opt.add_argument('--repeat',type=int,default=TrialParameters.repeat,
                        metavar='repeat::int',
                        help='set the number of times to repeat the '+\
                        'perturbation pattern')
pert_opt.add_argument('--dot-density',type=float,default=TrialParameters.dot_density,
                        metavar='density::dots/deg**2',
                        help='set the dots density')
pert_opt.add_argument('--ndots',type=int,default=TrialParameters.ndots,
                        metavar='dots::int',
                        help='set the number of dots -- will override dot density')
pert_opt.add_argument('--dot-size',metavar='size::deg',
                        type=float,default=TrialParameters.dot_size,
                        help='set the dot size')
pert_opt.add_argument('--filter-cut-off',type=float,
                        default=TrialParameters.filter_cut_off,
                        metavar='frequncy::Hz',
                        help='set the cut off frequency of the filter')
pert_opt.add_argument('--segment-duration',nargs='+',default=TrialParameters.segment_duration,
                        type=int,metavar='duration::frames',
                        help='set segment durations in units of frames; '+\
                        'if multiple values '+\
                        'are given, they are assigned in order to the '+\
                        'perturbation segments, if one value is given it '+\
                        'is assigned to all segments')
pert_opt.add_argument('--noise-update',default=TrialParameters.noise_update,
                        type=int,metavar='interval::frames',
                        help='set the update interval in frames between perturbations')

# screen parameters
screen_opt=parser.add_argument_group('Screen Parameters')
screen_opt.add_argument('--resolution',type=int,nargs=2,default=TrialParameters.resolution,
                        metavar=('width::deg','height::deg'),
                        help='set the display width and height in pixels')
screen_opt.add_argument('--screen-size',type=float,nargs=2,default=TrialParameters.screen_size,
                        metavar=('width::cm','height::cm'),
                        help='set the display width and height in cm')
screen_opt.add_argument('--refresh-rate',type=int,default=TrialParameters.refresh_rate,
                        metavar='REFRESH_RATE::Hz',
                        help='set the monitor refresh rate')
screen_opt.add_argument('--dist-to-eye',type=float,default=TrialParameters.dist_to_eye,
                        metavar='DIST_TO_EYE::cm',
                        help='set the distance to eye in cm')

depr=parser.add_argument_group('Deprecated')
depr.add_argument('--pert-mean',type=float,default=TrialParameters.pert_mean,
                        metavar='mu::deg',nargs='+',
                        help='set the mean of the perturbation hyper '+\
                        'distribution')

# General
parser.add_argument('-v','--verbose',type=int,default=TrialParameters.verbose,
                    choices=[0,1,2,3],
                    help='set verbosity level. 0 prints nothing whatsoever, '+\
                        '1 prints basic progress, 2 prints commands, '+\
                        '3 prints all avconv output')
parser.add_argument('--save-path',type=str,default=TrialParameters.save_path,
                    help='set the trial save path')

xor=lambda A, B : ((not A) and B) or (A and (not B)) 

## Overwrite file argument converter
def convert_arg_line_to_args(arg_line):
    for arg in arg_line.split():
        if not arg.strip():
            continue
        yield arg

parser.convert_arg_line_to_args = convert_arg_line_to_args

def parse(stdin,namespace):
    if xor('--resolution' in stdin,'--screen-size' in stdin):
        error_msg='Specify both or neither --resolution and '+\
                    '--screen-size'
        raise ValueError(error_msg)
    args = parser.parse_args(stdin,namespace)

    return vars(args)

if __name__ == '__main__':
    parse(sys.argv[1:])


