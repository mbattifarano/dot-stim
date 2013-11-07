import operator as op
import math
import os
import time

class TrialParameters(object):
    resource_path     = 'resources'
    #trial_path        = 'trial'
    #png_path          = '{}/png'.format(trial_path)
    #ndots             = 350
    #res               = [1024,768]
    dot_size          = 0.25

    trial_name        = 'noisy_field-'+time.strftime('%Y:%m:%d:%H:%M:%S')
    angle             = [0.0]
    angle_var         = [0.0]
    field_size        = 5
    field_center      = [0.0,0.0]
    speed             = [10.0]
    speed_var         = [0.0]
    window_speed      = [0.0]
    fix_dur           = 100

    pert_gain         = [0.0]
    pert_var          = [0.0]
    repeat            = 1
    dot_density       = 4
    ndots             = None
    #dot_size          = [0.25,0.25]
    filter_cut_off    = 32
    segment_duration  = [100]

    resolution        = [1024,768]
    screen_size       = [48.2,30.8]
    refresh_rate      = 100
    dist_to_eye       = 82

    pert_mean         = [0.0]
    verbose           = 1
    save_path         = 'trials'

    noise_update      = 4

    def __init__(self):
        self.px_per_cm = map(op.div,self.resolution,self.screen_size)
        self.cm_per_px = map(op.div,self.screen_size,self.resolution)
        self.deg_to_cm = lambda deg : self.dist_to_eye * math.tan(math.radians(deg))
        self.cm_to_deg = lambda cm  : math.degrees(math.atan2(cm,self.dist_to_eye))

        self.deg_to_px = lambda deg,i=0 : self.px_per_cm[i] * self.deg_to_cm(deg)
        self.px_to_deg = lambda px,i=0  : self.cm_to_deg(self.px_to_cm[i] * px)

        self.trial_path = '/'.join([self.save_path,self.trial_name])
        self.png_path   = '/'.join([self.trial_path,'png'])
        self.avi_path   = '/'.join([self.trial_path,'avi'])
        
        self.ndots = self.ndots or int(round(math.pi*(self.field_size**2)*self.dot_density))
        
        os.mkdir(self.trial_path)
        os.mkdir(self.png_path)
        os.mkdir(self.avi_path)

        self.seg_args=['segment_duration','pert_gain', 'pert_mean',
                         'pert_var','speed','speed_var',
                         'angle','angle_var', 'window_speed']



        self.pattern_len = self.get_pat_len(self.seg_args)
        map(self.expand_segment_args(),self.seg_args)
        #print self.window_speed
        self.dt=1/float(self.refresh_rate)
    
    def get_pat_len(self,attributes):
        return max(map(len,map(self.__getattribute__,attributes)))

    def expand_segment_args(self):
        pat_len =self.pattern_len
        def expand_seg_arg(opt):
            if type(getattr(self,opt))==list:
                if len(getattr(self,opt))==1:
                    setattr(self,opt,self.repeat*pat_len*getattr(self,opt))
                elif len(getattr(self,opt))==pat_len:
                    setattr(self,opt,self.repeat*getattr(self,opt))
                else:
                    raise TypeError('{} should either be scalar, or of length '+\
                                'pert_gain')
            else:
                print '{}: {}'.format(opt,type(getattr(self,opt)))
                raise TypeError('Something wicked happened')
            return 0
        return expand_seg_arg



