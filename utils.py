import operator as op
import subprocess as sh
import math

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

    def deg_to_px(self,deg):
        self.tupcheck(deg)
        cm=self.tupmap(self.PRM['deg_to_cm'],deg)
        px=self.cm_to_px(cm)
        return self.tupmap(self.float_to_int,px)

    def tupcheck(self,var):
        if (type(var)==type(())) & (len(var)==2):
            return 0
        else:
            raise TypeError('2-tuple required')

    def tupmap(self,*args):
        #map(self.tupcheck,args[1:]) # should only be used with 2-tuples
        return tuple(map(*args))

    def pos_mask(self,im):
    # specify pixel coordinates with origin at center and translate to PIL
    # coordinate system (origin top left)
        im_center=self.tupmap(op.div,im.size,(-2.0,2.0))
        pt=self.tupmap(op.add,im.pos,im_center)
        offset=self.tupmap(op.div,self.PRM['resolution'],(2.0,2.0))
        pt_flip=map(op.mul,(1,-1),pt)
        PIL_tuple=self.tupmap(self.float_to_int,map(op.add,offset,pt_flip))
        return PIL_tuple

    def avconv(self,path,name):
        frate=self.PRM['refresh_rate']
        cmd_str = 'avconv -r {0} -i ./{1}/%06d.png -r {0} -q 1 {2}/{3}.avi'
        cmd=cmd_str.format(frate,path,self.PRM['avi_dir'],name)
        print cmd
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
