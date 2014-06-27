import MakeTrial
import argparse
import textwrap
import ReadStdIn
import sys
import math
import random
import subprocess as sh
import time

wrap=lambda s : textwrap.fill(s,80)
with open('MakeTrial2.readme') as f:
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

parser=argparse.ArgumentParser( description=desc,
                                prefix_chars=':',
                                formatter_class=CustomHelpFormatter)

parser.add_argument(':x','::cross',nargs='*',type=str,default='')
parser.add_argument(':+','::add',nargs='*',type=str,default='')
parser.add_argument(':l','::loop',nargs='*',type=str,default='')
#parser.add_argument(':*','::inner',nargs='*',type=str,default='')
parser.add_argument(':r','::rand',action='store_true')
parser.add_argument(':s','::sample-size',type=int,default=1)

def get_arg_list(parser):
    actions = parser._actions
    arg_list=[]
    narg_list=[]
    for action in actions:
        nargs=action.nargs
        opt_str=action.option_strings
        if type(nargs)==int:
            n=nargs
        else:
            n=1
        narg_list.extend([n]*len(opt_str))
        arg_list.extend(opt_str)
    return arg_list, narg_list

def parse_MakeTrial_args(args_list):
    arg_list, N = get_arg_list(ReadStdIn.parser)

    value=[]
    parsed=[]
    for string in args_list[::-1]:
        if string in arg_list:
            parsed.append((string,value[::-1],len(value)))
            value=[]
        else:
            value.append(string)
    return parsed[::-1]
    
def sums(*args):
    add = lambda a,b: a+b
    try:
        s=reduce(add,args)
    except TypeError:
        s=0
    return s

def prods(*args):
    prod = lambda n,m : n*m
    try:
        p=reduce(prod,args)
    except:
        p=1
    return p    

def generate_loop_args(loop_args,other_args):
    arg_list, Nargs = get_arg_list(ReadStdIn.parser)
    nargs_per = [Nargs[arg_list.index(name)] for name,vals,N in loop_args]
    lens = [N/Nargs[arg_list.index(name)] for name,vals,N in loop_args]
    arg_no=1
    pass_args=[]
    for name, vals, N in loop_args:
        step=nargs_per[arg_no-1] # how many args each call will take
        P_in=prods(*lens[arg_no:])
        P_out=prods(*lens[0:arg_no-1])
        vals=[vals[i:i+step] for i in range(0,len(vals),step)] # list of lists
        new_vals=[name+' '+' '.join(val) for val in vals]
        exp_vals = sums(*[[val]*P_in for val in new_vals])*P_out
        if len(pass_args)==0:
            pass_args=[other_args+' '+val for val in exp_vals]
        else:
            pass_args=[old+' '+new for old,new in zip(pass_args,exp_vals)]
        arg_no+=1
    if len(pass_args)==0:
        pass_args=[other_args]
    return pass_args

def expand_cross_args(parsed_cross_args,randomize=False):
    lens = [tup[-1] for tup in parsed_cross_args]
    arg_no=1
    pass_args=[]
    index = range(prods(*lens))
    if randomize:
        random.shuffle(index)
    for name,vals,N in parsed_cross_args:
        P_in=prods(*lens[arg_no:])
        P_out=prods(*lens[0:arg_no-1])
        #new_vals = sums(*[(val+' ')*P_in for val in vals])*P_out
        exp_vals = sums(*[[val]*P_in for val in vals])*P_out
        ord_vals=[exp_vals[i] for i in index] 
        # if randomize is true index is a permuation, 
        # else it is range(N)
        new_vals = ' '.join(ord_vals) 
        pass_args.append(sums(name,' ',new_vals))
        arg_no+=1
    return ' '.join(pass_args), prods(*lens)

def int_div(n,m):
    q=int(math.floor(n/m))
    r=n-m*q
    return (q,r)

def expand_add_args(parsed_add_args,N):
    EXP='..'
    pass_args=[]
    for name,vals,nargs in parsed_add_args:
        if EXP in vals:
            if vals[-1]==EXP: # ie '..' at the end of arguments
                pattern=vals[:-1]
                q,r=int_div(N,len(pattern))
                new_vals = q*(' '.join(pattern)+' ')+' '.join(pattern[:r])
            elif vals[1]==EXP and len(vals)==3: 
            # MUST be in the middle of exactly two arguments
                LB=eval(vals[0])
                UB=eval(vals[2])
                step=(UB-LB)/float(N-1)
                new_vals=[type(LB)(LB+step*i) for i in range(N)]
                new_vals=' '.join(map(str,new_vals))
            else:
                raise TypeError('.. must be used at the end of a sequence '+\
                                'of arguments or in-between exactly two '+\
                                'arguments.')
            pass_args.append(sums(name,' ',new_vals))
        else:
            pass_args.append(sums(name,' ',' '.join(vals)))
    return ''.join(pass_args)


def main(arg_array):
    meta_args=parser.parse_args(arg_array)
    print_date='batch_generated-'+time.strftime('%Y:%m:%d:%H:%M:%S')
    output=[]
    trial_dir=''
    for i in range(meta_args.sample_size):
        cross_args = parse_MakeTrial_args(meta_args.cross)
        pass_c_args, N = expand_cross_args(cross_args,meta_args.rand)
        #print 'cross',pass_c_args
        add_args = parse_MakeTrial_args(meta_args.add)
        pass_a_args = expand_add_args(add_args,N)
        #print 'add', pass_a_args
        loop_args = parse_MakeTrial_args(meta_args.loop)
        # process loop args
        trial_args=pass_c_args+' '+pass_a_args
        parsed_loop_args = generate_loop_args(loop_args,trial_args)
        for args in parsed_loop_args:
            trial_name='noisy_field-'+time.strftime('%Y:%m:%d:%H:%M:%S')
            args+=' --trial-name {}'.format(trial_name)
            print args
            trial_dir=MakeTrial.main(args.split())
            output.append(trial_dir+' : '+args)
    with open('trials/{}'.format(print_date),'w') as log:
        log.write('\n'.join(output))
    return 0

if __name__=='__main__':
    main(sys.argv[1:])
