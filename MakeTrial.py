from PIL import Image, ImageEnhance
import sys
import operator as op
import math
import random as rand
import os
import handle_args
import subprocess as sh
import scipy.io as sio
from copy import deepcopy
import matlab
import utils

RECORD={} # frame-based data storage
VERSION=2.0

def main(arg_array):
    global PRM
    global conv
    global RECORD
    global dblevel

    PRM, conv = handle_args.get_params(arg_array)
    
    dblevel=utils.DebugLevels()
    conv.stdout_write("MakeTrial {}".format(VERSION),dblevel.progress)

    prnt_str="Saving config... [{}/args]".format(PRM['trial_dir'])
    conv.stdout_write(prnt_str,dblevel.progress)
    handle_args.arg_array_to_file(arg_array,PRM['trial_dir'])
    RECORD = conv.init_global_record(PRM)

    try:
        generate_trial()
        
        mat_file_dest='{}/raw.mat'.format(PRM['trial_dir'])
        prnt_str="Saving to mat file... [{}]".format(mat_file_dest)
        conv.stdout_write(prnt_str,dblevel.progress)
        sio.savemat(mat_file_dest,RECORD,oned_as='column')

        conv.stdout_write("Formatting raw data...",dblevel.progress)
        matlab.matlab('format_raw',PRM['trial_dir'],verbose=PRM['verbose'])
        
        conv.stdout_write("Trial complete.",dblevel.progress)
    except KeyboardInterrupt:
        conv.stdout_write('KeyboardInterrupt: Removing trial directory...',
                                dblevel.essential)
        sh.check_call(['rm','-r',PRM['trial_dir']])
        sys.exit()
    return 0

def generate_angles():
    n_dirs=PRM['n_dirs']
    angle=360/float(n_dirs)
    base_angle=PRM['base_angle']
    return [(base_angle + i*angle) % 360 for i in range(n_dirs)]

def get_dot_noise(sigma,hm,hs): # hm and hs are hyper parameters
    n_dots = PRM['n_dots']
    gauss = rand.gauss
    m = gauss(hm,hs)
    return [gauss(m,sigma) for i in range(n_dots) ]

def generate_dot_noise(sigma,hm,hs,y_prev):
    noise_mag = get_dot_noise(sigma,hm,hs)
    if len(y_prev)==0:
        y_prev=[0]*len(noise_mag)
    return map(conv.lowpass,noise_mag,y_prev)

def move(DOTS,direction,sigma,hm,hs,y_prev,speed):
    cos=math.cos
    sin=math.sin
    tupmap=conv.tupmap
    dt=1/float(PRM['refresh_rate'])
    rho=float(speed)
    angle=math.radians(direction)
    unit_dir=(cos(angle),sin(angle))
    # get step
    step=conv.deg_to_px(tupmap(op.mul,(rho,rho),unit_dir))
    # get noise
    ns_dir=math.radians(direction+90)
    noise_mag=generate_dot_noise(sigma,hm,hs,y_prev) 
    noise_vec=[tupmap(op.mul,(ns,ns),(cos(ns_dir),sin(ns_dir))) \
                                            for ns in noise_mag]
    noise_vec=tupmap(conv.deg_to_px,noise_vec)
    # add noise to step
    step_vec=[tupmap(op.add,step,ns) for ns in noise_vec]
    # multiply by dt
    step_vec=[tupmap(op.mul,el,(dt,dt)) for el in step_vec]
    # update dot.pos
    for dot, delta in zip(DOTS,step_vec):
        newpos=tupmap(op.add,dot.pos,delta)
        dot.pos=screen_wrap(newpos)
    return DOTS, noise_mag

def screen_wrap(xypos):
    x,y=conv.tupmap(conv.float_to_int,xypos)
    w,h=PRM['resolution']
    hw = conv.float_to_int(w/2.0)
    hh = conv.float_to_int(h/2.0)
    wx = ( (x+hw) % w)-hw
    wy = ( (y+hh) % h)-hh
    return (wx,wy)

def generate_segment(DOTS,direction,sigma,hm,hs,duration,path,speed):
    global RECORD
    global FRAME_NO
    #nframes=conv.float_to_int(PRM['refresh_rate']*duration*0.001)
    nframes=duration
    FRAME=new_frame()
    DOTS=render_dot_field(FRAME,path,DOTS)
    noise_mag=[0]*len(DOTS)
    RECORD['trial']['dots'].append([list(dot.pos) for dot in DOTS])
    RECORD['trial']['noise'].append(noise_mag)
    for frame in range(nframes):
        FRAME=new_frame()
        DOTS,noise_mag=move(DOTS,direction,sigma,hm,hs,noise_mag,speed)
        str_frame="frame_{}".format(FRAME_NO)
        RECORD['trial']['dots'].append([list(dot.pos) for dot in DOTS])
        RECORD['trial']['noise'].append(noise_mag)
        render_dot_field(FRAME,path,DOTS)
    return DOTS

def generate_fixation(DOTS,path):
    duration = PRM['fix_dur']
    DOTS = generate_segment(DOTS,0,0,0,0,duration,path,0)
    return DOTS

def generate_trial():
    global FRAME_NO
    global RECORD
    # unpack values
    gauss=rand.gauss
    FRAME_NO=0
    RECORD['trial']={'dots':[],'noise':[], 'diode':[]}
    path=PRM['png_dir']
    seg_params=zip(*map(PRM.get,PRM['segment_args']))

    conv.stdout_write("Generating trial...",dblevel.progress)

    DOTS=generate_fixation([],path)
    for dur,sigma,hm,hs,spd,spd_var,ang,ang_var in seg_params:
        speed=gauss(spd,spd_var)
        angle=gauss(ang,ang_var)
        DOTS=generate_segment(DOTS,angle,sigma,hm,hs,dur,path,speed)
    DOTS=generate_fixation(DOTS,path)
    conv.stdout_write("Compiling to avi...",dblevel.progress)
    conv.avconv(path,angle)

def new_frame():
    MODE='RGB'
    SIZE=PRM['resolution']
    COLOR='black'
    base_im=Image.new(MODE,SIZE,COLOR)
    CENTER=get_dot(im_file='circle-red',xypos=(0,0),scale=2)
    place_dot(base_im,CENTER)
    # add calib square based on FRAME_NO
    return base_im

def get_calibration_square(scale=1,lum=-1):
    global RECORD
    sq_pos=conv.tupmap(op.div,PRM['resolution'],[2.0,2.0])
    sq_pos=conv.tupmap(op.mul,sq_pos,[1,-1])
    if lum == -1:
        lum = ((FRAME_NO % 4)+2)/5.0
        RECORD['trial']['diode'].append(lum)
    SQUARE=get_dot(im_file='square',xypos=sq_pos,scale=scale,brightness=lum)
    SQUARE=SQUARE.convert('RGB')
    SQUARE.pos=sq_pos
    w,h = SQUARE.size
    pad=4
    SQUARE.pos=conv.tupmap(op.add,SQUARE.pos,(-(0.5*w+pad),0.5*h+pad))
    return SQUARE

def save_frame(image,path):
    global FRAME_NO
    filename='{}/{:06d}.png'.format(path,FRAME_NO)
    image.save(filename)
    FRAME_NO+=1
    return 0

def render_dot_field(frame,path,DOTS=[]):
    paste_in_frame = lambda im : place_dot(frame,im,mask=True)
    ndots=PRM['n_dots']
    if len(DOTS)==0:
        DOTS=[get_dot() for i in range(ndots)]
    map(paste_in_frame,DOTS)

    sq_base=get_calibration_square(scale=10,lum=0)
    place_dot(frame,sq_base)
    SQUARE=get_calibration_square(scale=10)
    place_dot(frame,SQUARE)
    
    save_frame(frame,path)
    return DOTS
    
def place_dot(BG,dot,mask=False):
    pos=conv.pos_mask(dot)
    if mask:
        BG.paste(dot,pos,dot)
    else:
        BG.paste(dot,pos)
    return 0

def get_dot(im_file='circle',xypos=(),scale=1,brightness=1.0):
    dot=Image.open('resources/{}.png'.format(im_file))
    dot=dot.convert('RGBA')
    dot_size=conv.deg_to_px(conv.tupmap(op.mul,PRM['dot_size'],(scale,scale)))
    dot=dot.resize(dot_size,Image.ANTIALIAS)
    ch_lum=ImageEnhance.Brightness(dot)
    dot=ch_lum.enhance(brightness)
    if xypos:
        conv.tupcheck(xypos)
        pos=xypos
    else:
        LB=map(op.mul,(-1,-1),PRM['field_limits'])
        UB=PRM['field_limits']
        pos=conv.tupmap(rand.randrange,LB,UB,dot_size)
    dot.pos=pos # create pos attribute -- IN PIXELS
    return dot

if __name__ == '__main__':
    main(sys.argv[1:])
