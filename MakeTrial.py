from PIL import Image
import sys
import operator as op
import math
import random as rand
import os
import handle_args
import subprocess as sh
#import numpy as np

def main(arg_array):
    global PRM
    global conv

    print "MakeTrial 1.0"
    print "Reading arguments..."
    PRM, conv = handle_args.get_params(arg_array)
    print "Saving config... [{}]".format(PRM['trial_dir']+'/args')
    handle_args.arg_array_to_file(arg_array,PRM['trial_dir'])
    #try:
    generate_trial()
    #except:
    #    print sys.exc_info()
    #    sh.check_call(['rm','-r',PRM['trial_dir']])
    return 0

def generate_angles():
    n_dirs=PRM['n_dirs']
    angle=360/float(n_dirs)
    base_angle=PRM['base_angle']
    return [(base_angle + i*angle) % 360 for i in range(n_dirs)]

def generate_dot_noise(sigma,hm,hs): # hm and hs are hyper parameters
    n_dots = PRM['n_dots']
    xs,ys = sigma
    gauss = rand.gauss
    mx,my = map(gauss,hm,hs)
    return [(gauss(mx,xs),gauss(my,ys)) for i in range(n_dots) ]

def move(DOTS,direction,sigma,hm,hs):
    dt=1/float(PRM['refresh_rate'])
    rho=float(PRM['speed'])
    spd=conv.deg_to_px((rho,rho))
    gain=conv.deg_to_px((sigma,sigma))
    hm,hs = map(conv.deg_to_px,[(hm,hm),(hs,hs)])
    angle=math.radians(direction)
    unit_dir=(math.cos(angle),math.sin(angle))

    step=conv.tupmap(op.mul,spd,unit_dir) #::(float,float)
    # get noise
    ns_dir=math.radians(direction+90)
    noise_vec=[conv.tupmap(op.mul,ns,(math.cos(ns_dir),math.sin(ns_dir)))\
                    for ns in generate_dot_noise(gain,hm,hs) ]
    # add noise
    step_vec=[conv.tupmap(op.add,step,ns) for ns in noise_vec]
    step_vec=[conv.tupmap(op.mul,el,(dt,dt)) for el in step_vec]
    # update dot.pos
    for dot, delta in zip(DOTS,step_vec):
        newpos=conv.tupmap(op.add,dot.pos,delta)
        dot.pos=screen_wrap(newpos)
    return DOTS #technically unnecessary since DOTS is modified globally

def screen_wrap(xypos):
    x,y=conv.tupmap(conv.float_to_int,xypos)
    w,h=PRM['resolution']
    hw = conv.float_to_int(w/2.0)
    hh = conv.float_to_int(h/2.0)
    wx = ( (x+hw) % w)-hw
    wy = ( (y+hh) % h)-hh
    return (wx,wy)

def generate_segment(DOTS,direction,sigma,hm,hs,duration,path):
    nframes=conv.float_to_int(PRM['refresh_rate']*duration*0.001)
    FRAME=new_frame()
    DOTS=render_dot_field(FRAME,path,DOTS)
    for frame in range(nframes):
        FRAME=new_frame()
        DOTS=move(DOTS,direction,sigma,hm,hs)
        render_dot_field(FRAME,path,DOTS)
    return DOTS

def generate_trial():
    global FRAME_NO
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
    return base_im

def save_frame(image,path):
    global FRAME_NO
    filename='{}/{:06d}.png'.format(path,FRAME_NO)
    image.save(filename)
    FRAME_NO+=1
    return 0

def render_dot_field(frame,path,DOTS=[]):
    paste_in_frame = lambda im : place_dot(frame,im)
    ndots=PRM['n_dots']
    if len(DOTS)==0:
        DOTS=[get_dot() for i in range(ndots)]
    map(paste_in_frame,DOTS)
    save_frame(frame,path)
    return DOTS
    
def place_dot(BG,dot):
    BG.paste(dot,conv.pos_mask(dot))
    return 0

def get_dot(im_file='circle',xypos=(),scale=1):
    dot=Image.open('resources/{}.png'.format(im_file))
    dot_size=conv.deg_to_px(conv.tupmap(op.mul,PRM['dot_size'],(scale,scale)))
    dot=dot.resize(dot_size,Image.ANTIALIAS)
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
