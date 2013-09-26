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

RECORD={} # frame-based data storage

def main(arg_array):
    global PRM
    global conv
    global RECORD

    print "MakeTrial 1.0"
    print "Reading arguments..."
    PRM, conv = handle_args.get_params(arg_array)
    print "Saving config... [{}/args]".format(PRM['trial_dir'])
    handle_args.arg_array_to_file(arg_array,PRM['trial_dir'])
    
    RECORD['config']=deepcopy(PRM)
    del RECORD['config']['deg_to_cm']
    del RECORD['config']['cm_to_deg']
    RECORD['trials']={}
    #try:
    generate_trial()
    print RECORD['trials']['dir0_0'].keys()
    print "Saving to mat file... [{}/main.mat]".format(PRM['trial_dir'])
    sio.savemat("{}/main.mat".format(PRM['trial_dir']),RECORD,oned_as='row')
    #except:
    #    print sys.exc_info()
    #    sh.check_call(['rm','-r',PRM['trial_dir']])
    print "Trial complete."
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

def move(DOTS,direction,sigma,hm,hs,y_prev):
    cos=math.cos
    sin=math.sin
    tupmap=conv.tupmap
    dt=1/float(PRM['refresh_rate'])
    rho=float(PRM['speed'])
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

def generate_segment(DOTS,direction,sigma,hm,hs,duration,path):
    global RECORD
    global FRAME_NO
    str_dir='dir{}'.format(direction)
    str_dir=str_dir.replace('.','_')
    nframes=conv.float_to_int(PRM['refresh_rate']*duration*0.001)
    FRAME=new_frame()
    DOTS=render_dot_field(FRAME,path,DOTS)
    str_frame="frame_{}".format(FRAME_NO-1)
    RECORD['trials'][str_dir][str_frame]=[list(dot.pos) for dot in DOTS]
    noise_mag=[]
    for frame in range(nframes):
        FRAME=new_frame()
        DOTS,noise_mag=move(DOTS,direction,sigma,hm,hs,noise_mag)
        str_frame="frame_{}".format(FRAME_NO)
        RECORD['trials'][str_dir][str_frame]=[list(dot.pos) for dot in DOTS]
        render_dot_field(FRAME,path,DOTS)
    return DOTS

def generate_trial():
    global FRAME_NO
    global RECORD
    dirs=generate_angles()
    base_path=PRM['png_dir']
    print "Generating trialset..."
    for angle in dirs:
        FRAME_NO=0
        print "Generating png files for {} degree trial...".format(angle)
        path = '{}/{:0.2f}'.format(base_path,angle)
        os.mkdir(path)
        DOTS=[]
        seg_params=zip(*map(PRM.get,['segment_duration',
                                     'pert_gain',
                                     'pert_mean',
                                     'pert_var']))
        str_dir='dir{}'.format(angle)
        str_dir=str_dir.replace('.','_')
        RECORD['trials'][str_dir]={}
        for dur,sigma,hm,hs in seg_params:
            DOTS=generate_segment(DOTS,angle,sigma,hm,hs,dur,path)
        print "Compiling to avi..."
        conv.avconv(path,angle)

def new_frame():
    MODE='RGB'
    SIZE=PRM['resolution']
    COLOR='black'
    base_im=Image.new(MODE,SIZE,COLOR)
    CENTER=get_dot(im_file='circle-red',xypos=(0,0),scale=2)
    place_dot(base_im,CENTER)
    # add calib square based on FRAME_NO
    SQUARE=get_calibration_square(scale=10)
    place_dot(base_im,SQUARE)
    return base_im

def get_calibration_square(scale=1):
    sq_pos=conv.tupmap(op.div,PRM['resolution'],[2.0,2.0])
    sq_pos=conv.tupmap(op.mul,sq_pos,[1,-1])
    lum=(FRAME_NO % 5)/4.0
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
