import operator as op
import subprocess as sh
import math
from copy import deepcopy
import sys

class Utils:
    def __init__(self,PRM):
        self.PRM=PRM

    def float_to_int(self,f): 
        return int(round(f))

    def cm_to_px(self,cm):
    # returns cm co-ordinates (from center) in pixels
        self.tupcheck(cm)
        in_px=map(op.mul,cm,self.PRM['px_per_cm'])
        return self.tupmap(self.float_to_int,in_px)
        
    def px_to_cm(self,px):
    # returns pixel co-ordinates in cm from center of screen
        self.tupcheck(px)
        return self.tupmap(op.mul,px,self.PRM['cm_per_px'])

    def px_to_deg(self,px):
        self.tupcheck(px)
        cm=self.px_to_cm(px)
        deg=map(self.PRM['cm_to_deg'],cm)
        return tuple(deg)

    def deg_to_px(self,deg,scalar=False):
        if not scalar:
            self.tupcheck(deg)
        else:
            deg=(deg,0)
        cm=self.tupmap(self.PRM['deg_to_cm'],deg)
        px=self.cm_to_px(cm)
        deg_pos=self.tupmap(self.float_to_int,px)
        if not scalar:
            return deg_pos
        else:
            return deg_pos[0]

    def tupcheck(self,var):
        if (type(var)==type(())) & (len(var)==2):
            return 0
        else:
            raise TypeError('2-tuple required')

    def tupmap(self,*args):
        #map(self.tupcheck,args[1:]) # should only be used with 2-tuples
        return tuple(map(*args))

    def from_polar(self,polar):
        rho,theta = polar

        x=round(rho*math.cos(theta))
        y=round(rho*math.sin(theta))
        return (x,y)

    def to_polar(self,xy):
        x,y=xy
        rho=(x**2 + y**2)**0.5
        theta=math.atan2(y,x)
        return (rho,theta)

    def pos_mask(self,im,center=(0.0,0.0)):
    # specify pixel coordinates with origin at center and translate to PIL
    # coordinate system (origin top left)
        im_center=self.tupmap(op.div,im.size,(-2.0,2.0))
        pt=self.tupmap(op.add,im.pos,im_center)
        offset=self.tupmap(op.div,self.PRM['resolution'],(2.0,2.0))
        pt_flip=map(op.mul,(1,-1),pt)
        cart_tuple=map(op.add,offset,pt_flip)
        center=map(op.mul,(1,-1),center)
        #center=(5,5)
        PIL_tuple=self.tupmap(self.float_to_int,map(op.add,center,cart_tuple))
        return PIL_tuple

    def avconv(self,path,name):
        frate=self.PRM['refresh_rate']
        cmd_str = 'avconv -r {0} -i ./{1}/%06d.png -r {0} -q 1 {2}/{3}.avi '+\
                    '2> {2}/avconv.{3}.log'*(self.PRM['verbose']<3) 
        cmd=cmd_str.format(frate,path,self.PRM['avi_dir'],name)
        self.stdout_write(cmd,2)
        sh.check_call(cmd,shell=True)
        return 0

    def lowpass(self,x_now,y_prev=0):
        # see the wikipedia article for low pass filters for 
        # implementation details
        fc = float(self.PRM['filter_cut_off'])
        fs = float(self.PRM['refresh_rate'])

        RC = 1/(2*math.pi*fc)
        dt = 1/fs
        y_now = float(x_now) * (dt/(RC+dt)) + float(y_prev) * (RC/(RC+dt))
        return y_now
        
    def init_global_record(self,params):
        RECORD={}
        RECORD['config']=deepcopy(params)
        RECORD['config']['SegStart']=[]
        RECORD['trial']={'dots':[], 'noise':[], 'diode':[]}

        # Add entries:
        #RECORD['trial']={} # no longer necessary to initialize

        # Remove entries:
        del RECORD['config']['deg_to_cm']
        del RECORD['config']['cm_to_deg']

        return RECORD

    def stdout_write(self,prnt_str,debug_level):
        prnt_str=prnt_str.strip('\n')
        prnt_str+='\n'
        sys.stdout.write(prnt_str*(self.PRM['verbose']>=debug_level))

class DebugLevels:
    def __init__(self):
        self.essential=0
        self.progress=1
        self.progress_detail=2
        self.command=2
        self.detail=3
