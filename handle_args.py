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
    PRM['trial_dir']=PRM['trial_save_path']+'/'+PRM['trial_name']
    PRM['png_dir']=PRM['trial_dir']+'/png'
    PRM['avi_dir']=PRM['trial_dir']+'/avi'

    os.mkdir(PRM['trial_dir'])
    os.mkdir(PRM['png_dir'])
    os.mkdir(PRM['avi_dir'])

    # type-correct and change pert_gain list to account for repeat
    if type(PRM['pert_gain'])==float:
        PRM['pert_gain']=PRM['repeat']*[PRM['pert_gain']]
    elif type(PRM['pert_gain'])==list:
        PRM['pert_gain']=PRM['repeat']*PRM['pert_gain']
    else:
        print 'pert_gain: {}'.format(type(PRM['pert_gain']))
        raise TypeError('Something wicked happened')
    # type-correct and account for repeats
    if type(PRM['segment_duration'])==int:
        print "HELLO"
        PRM['segment_duration']=len(PRM['pert_gain'])*[PRM['segment_duration']]
    elif type(PRM['segment_duration'])==list:
        if len(PRM['segment_duration'])==1:
            PRM['segment_duration']=len(PRM['pert_gain'])*\
                                        PRM['segment_duration']
        else: 
            PRM['segment_duration']=PRM['repeat']*PRM['segment_duration']
    else:
        print 'duration: {}'.format(type(PRM['segment_duration']))
        raise TypeError('Something wicked happened')
        
    # if duration list and pert_gain list are NOT the same length, something
    # went horribly wrong (shouldn't happen)
    if not (len(PRM['pert_gain'])==len(PRM['segment_duration'])):
        print PRM['pert_gain']
        print PRM['segment_duration']
        raise TypeError('pert_gain and duration are not the same length')

    return PRM, conv

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
    is_opt = lambda s : s.startswith('-')
    put_newline = lambda b : b*'\n'
    options = map(is_opt,arg_array) # array, options[i]=True iff arg_arry[i]
                                    # starts with '-'
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
    
    
