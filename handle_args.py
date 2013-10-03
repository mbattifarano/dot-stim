import ReadStdIn
import copy
import re
import utils
import operator as op
import math
import os

def get_params(arg_array):
    PRM=ReadStdIn.parse(arg_array)
    PRM['px_per_cm']=map(op.div,PRM['resolution'],PRM['screen_size'])
    PRM['cm_per_px']=map(op.div,PRM['screen_size'],PRM['resolution'])
    PRM['deg_to_cm']=lambda deg : (PRM['dist_to_eye']*\
                                    math.tan(math.radians(deg)))
    PRM['cm_to_deg']=lambda cm : (math.degrees(\
                                    math.atan2(cm,PRM['dist_to_eye'])))

    conv=utils.Utils(PRM)
    PRM['field_limits']=conv.deg_to_px(conv.tupmap(op.div,\
                                    PRM['field_size'],(2.0,2.0)))
    PRM['trial_save_path']='trials'
    PRM['trial_dir']=PRM['trial_save_path']+'/'+PRM['trial_name']
    PRM['png_dir']=PRM['trial_dir']+'/png'
    PRM['avi_dir']=PRM['trial_dir']+'/avi'

    os.mkdir(PRM['trial_dir'])
    os.mkdir(PRM['png_dir'])
    os.mkdir(PRM['avi_dir'])

    PRM['segment_args']=['segment_duration','pert_gain','pert_mean',
                         'pert_var','speed','speed_var']

    PRM['pat_len']=get_pat_len(PRM,PRM['segment_args'])

    map(expand_segment_args(PRM,PRM['pat_len']),PRM['segment_args'])
    
    return PRM, conv

def get_pat_len(PRM,segment_args):
    return max(map(len,map(PRM.get,segment_args)))

def expand_segment_args(PRM,pat_len):
    def expand_seg_arg(opt):
        if type(PRM[opt])==list:
            if len(PRM[opt])==1:
                PRM[opt]=PRM['repeat']*pat_len*PRM[opt]
            elif len(PRM[opt])==pat_len:
                PRM[opt]=PRM['repeat']*PRM[opt]
            else:
                raise TypeError('{} should either be scalar, or of length '+\
                                'pert_gain')
        else:
            print '{}: {}'.format(opt,type(PRM[opt]))
            raise TypeError('Something wicked happened')
        return 0
    return expand_seg_arg

def dict_to_arg_str(d):
# definitely a super sketch hack -- map return a list of `None' values
# since l.extend is an in-place list operator so l is the variable we want
    l=[]
    d=reformat_dict(d)
    map(l.extend,dict_to_arg_list(d))
    return ' '.join(map(str,l))

def dict_to_arg_list(d):
    d=reformat_dict(d)
    return map(list,zip(d.keys(),d.values()))

def arg_array_to_file(arg_array,path):
    is_opt = re.compile('--?[a-zA-Z-]+')
    put_newline = lambda m : bool(m)*'\n'
    options = map(is_opt.match,arg_array) #array, True for matches
    newlines = map(put_newline, options) # array, newlines[i]='\n' iff
                                         # options[i]=True, otherwise, ''
    fstr_list=[ symb+arg for symb,arg in zip(newlines,arg_array) ]
    fstr=' '.join(fstr_list)
    fstr=fstr.lstrip(' \n')
    with open('{}/args'.format(path),'w') as f:
        f.write(fstr)
    return 0

# Obsolete
#def dict_to_arg_file(d,path):
#    d=reformat_dict(d)
#    l=dict_to_arg_list(d)
#    l=[ ' '.join(map(str,el)) for el in l]
#    s='\n'.join(l)
#    with open('{}/args'.format(path),'w') as f:
#        f.write(s)
#    return s
#
## NOTE: reformat_dict(reformat(d))==reformat_dict(d)
def reformat_dict(d): return dict(zip(map(reformat_key,d.keys()),d.values()))

def reformat_key(key): return '--'+key.replace('--','').replace('_','-')
    
    
