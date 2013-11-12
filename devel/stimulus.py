import parser
import defaults
import random as rand
import math
import sys
import scipy.io as sio

class Trial(object): 
# Top level trial generator
    import video
    def __init__(self,*arg_array):
        # parse arg array using video.Base.dfns as namespace
        parameter_namespace=defaults.TrialParameters # the class, 
                                                     # NOT an instance
        parser.parse(arg_array,namespace=parameter_namespace)
        self.video.Base.dfns=parameter_namespace() # init the class; generates all
                                                   # dependent parameters
        self.stdout_write = self.video.Base.stdout_write
        self.vid = self.video.Video() # initialize a new video object
        self.target = self.video.DotField()
        self.record = self.video.Record()
        self.record.to_mat['dot_pos']=[]
        self.record.to_mat['objects']=[]
        self.record.to_mat['dot_size_px']=self.target.dots[0].image.image.size

    def generate(self):
        seg_params = zip(*map(self.vid.dfns.__getattribute__,
                                self.vid.dfns.seg_args))
        #print seg_params
        #self.generate_fixation()
        for seg_dfn in seg_params:
            seg_dict = dict(zip(self.vid.dfns.seg_args,seg_dfn))
            #print seg_dict
            self.generate_segment(seg_dict,show_target=True)
        if self.vid.dfns.end_jump:
            self.generate_end_fixation(show_target=True)
        else:
            self.generate_fixation()
        mat_path=self.vid.dfns.trial_path+'/'+self.vid.dfns.trial_name
        #print self.record.to_mat['dfns']
        sio.savemat(mat_path,self.record.to_mat)
        self.vid.compile_avi()

    def generate_segment(self,seg_dict,show_target=True):
        #print seg_dict
        for frame in range(seg_dict['segment_duration']):
            self.update_field_center(seg_dict)
            dPos = self.get_pos_update(seg_dict)
            self.update_frame(dPos,show_target)

    def update_field_center(self,seg_dict):
        dt = self.vid.dfns.dt
        rho = float(seg_dict['window_speed'])        
        theta = math.radians(seg_dict['angle'])
        #print dt,rho,theta
        dPos = self.video.Point()
        dPos.set_polar_pos(rho,theta)
        dPos.scale(dt)        
        self.target.move_field(dPos)
        #print dPos.pos,self.target.pos.pos
        
    def get_pos_update(self,seg_dict,noise=True):
        dt = self.vid.dfns.dt
        update_int=self.vid.dfns.noise_update
        if (self.vid.frame_no % update_int) == 0:
            self.speed_noise=self.get_speed_noise(0,seg_dict['speed_var'])
            self.angle_noise=self.get_angle_noise(0,seg_dict['angle_var'])
        
        dPos = self.generate_target_trajectory(seg_dict['angle'],seg_dict['speed'])
        [pt.scale(dt) for pt in dPos]
        return dPos

    def get_speed_noise(self,speed_mean,speed_var):
        adj_var = speed_var
        F=lambda x : (2**x)
        return [Noise(rand.uniform,[-adj_var,adj_var],fn=F) \
                    for i in range(self.target.ndots)]

    def get_angle_noise(self,angle,angle_var):
        return [Noise(rand.uniform,[angle-angle_var,angle+angle_var])\
                    for i in range(self.target.ndots)]
        
    def generate_target_trajectory(self,angle,speed):
        rho = float(speed)        
        theta = math.radians(angle)

        points=[]
        for n_spd,n_dir in zip(self.speed_noise,self.angle_noise):
            pt=self.video.Point()
            
            pt.set_polar_pos(rho*n_spd.value,theta+math.radians(n_dir.value))
            points.append(pt)
        return points
        
    def update_frame(self,dPos,show_target=True):
        self.target.move(dPos)
        objects_in_frame=[self.video.FixationDot()]#,
                            #self.video.CalibrationSquare()]
        if show_target:
            objects_in_frame=[self.target]
        self.vid.add_frame()
        self.vid.add_object(objects_in_frame)
        render_out = self.vid.render()
        self.record.to_mat['dot_pos'].append(render_out)
        self.record.to_mat['objects'].append(map(self.record._get_name,objects_in_frame))
        self.vid.write()

    def generate_fixation(self,show_target=False,dur=None):
        dur=dur or self.vid.dfns.fix_dur
        seg_dict={'segment_duration':dur,'pert_gain':0,'pert_mean':0,'pert_var':0,
                    'speed':0,'speed_var':0,'angle':0,'angle_var':0,
                    'window_speed':0}
        self.generate_segment(seg_dict,show_target)

    def generate_end_fixation(self,show_target=True):
        dur=self.vid.dfns.fix_dur-1
        self.target.move_field(self.video.Point(1,0))
        self.generate_fixation(show_target,dur)


class Noise(object):
    def __init__(self,dist,args,fn=(lambda x: x)):
        self.value = fn(dist(*args))

if __name__=='__main__':
    t=Trial(*sys.argv[1:])
    t.generate()

