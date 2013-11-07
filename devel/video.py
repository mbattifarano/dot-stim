from PIL import Image, ImageEnhance
import random
import defaults
import operator as op
import math
import sys
import subprocess as sh

class Base(object):
    dfns = defaults.TrialParameters
    def stdout_write(self,prnt_str,debug_level):
        prnt_str=prnt_str.strip('\n')
        prnt_str+='\n'
        sys.stdout.write(prnt_str*(self.dfns.verbose>=debug_level))

class Video(Base):
    def __init__(self):
        super(Video,self).__init__()
        self.frames=[]
        self.targets=[]
        self.frame_no=0

    def frame_no(self): return len(self.frames)

    def add_frame(self,*args,**kwargs):
        self.frame_no+=1
        self.frames.append(Frame(*args,frame_no=self.frame_no,**kwargs))

    def add_object_to_frame(self,drawables,frame_index=-1):
        self.frames[frame_index].add_object(drawables)

    def add_object(self,drawables):
        try:
            self.add_object_to_frame(drawables,-1)
        except IndexError:
            print "what?"
            self.add_frame(frame_no=len(self.frames))
            self.add_object_to_frame(drawables,-1)

    def add_target(self,*drawables):
        self.targets=drawables
        self.add_object(*drawables)

    def render(self):
        self.frames[-1].render()

    def write(self):
        self.frames[-1].write()

    def compile_avi(self):
        frate=self.dfns.refresh_rate
        name = self.dfns.trial_name
        path = self.dfns.avi_path
        cmd_str = 'avconv -r {0} -i ./{1}/%06d.png -r {0} -q 1 {2}/{3}.avi '+\
                    '2> {2}/avconv.{3}.log'*(self.dfns.verbose<3) 
        cmd=cmd_str.format(frate,self.dfns.png_path,self.dfns.avi_path,
                            self.dfns.trial_name)
        self.stdout_write(cmd,2)
        sh.check_call(cmd,shell=True)


class Frame(Base):
    def __init__(self,frame_no,image=None):
        super(Frame,self).__init__()
        self.objects=[]
        self.frame_no=frame_no
        self.color='black'
        if image:
            self.image=image
        else:
            self.set_background('RGB',self.dfns.resolution,self.color)

    def set_background(self,mode,size,color):
        self.image=Image.new(mode,size,color)
        self.color=color

    def add_object(self,drawables):
        self.objects.extend(drawables)

    def render(self):
        [obj.draw(self,mask=True) for obj in self.objects]
        #self.image.show()

    def write(self):
        filename='{}/{:06d}.png'.format(self.dfns.png_path,self.frame_no)
        self.image.save(filename)

class DotField(Base):
    def __init__(self,center=None,size=None,
                        ndots=None,bounds=None,
                        dot_size=None):
        super(DotField,self).__init__()
        center_pt = center or self.dfns.field_center
        self.pos=Point(*center_pt)
        self._apeture_im = 'circle'
        self.size = size or self.dfns.field_size
        self.ndots = ndots or self.dfns.ndots
        #self.bounds = bounds or dfns.resolution
        self.dot_size = dot_size or self.dfns.dot_size
        self.generate_dot_field(self.ndots,self.size)

    def generate_dot_field(self,ndots,size):
        unif = random.uniform
        self.dots = []
        for i in range(ndots):
            mag=2*size
            while mag >= (size - 0.1):
                x = unif(-size,size)
                y = unif(-size,size)
                mag=(x**2+y**2)**0.5
            new_dot = Sprite(xypos=(x,y),size=self.dot_size)
            #print new_dot.pos.pos
            self.dots.append(new_dot)

    def draw(self,frame,mask=False):
        [dot.draw(frame,self.pos,mask) for dot in self.dots]

    def move(self,dPos_list):
        size=self.dot_size
        [dot.move(dPos) \
            for dot,dPos in zip(self.dots,dPos_list)]
        map(self.field_wrap,self.dots)

    def field_wrap(self,point):
        rho, theta = point.pos.polar()
        if rho >= self.size:
            rho = self.size-0.1
            angle = random.uniform((3/4.0)*math.pi,(5/4.0)*math.pi)
            theta = (theta - angle) % 2*math.pi
        point.pos.set_polar_pos(rho,theta)

    def move_field(self,dPos):
        self.pos+=dPos

class ImageLoader(Base):
    def __init__(self,im_file,size=0.25,brightness=1.0):
        super(ImageLoader,self).__init__()
        self._image_file = im_file
        self.size = size
        self.brightness = brightness
        self.image = self._load_image()

    def _load_image(self):
        self._original_image = Image.open(self._image_file)
        this_image = self._original_image.convert('RGBA')
        this_image = self.adjust_scale(this_image)
        this_image = self.adjust_brightness(this_image)
        return this_image
        
    def adjust_brightness(self,im):
        chlum = ImageEnhance.Brightness(im)
        new_im = chlum.enhance(self.brightness)
        return new_im

    def adjust_scale(self,im):
        x=int(round(self.dfns.deg_to_px(self.size,i=0)))
        y=int(round(self.dfns.deg_to_px(self.size,i=1)))
        new_im = im.resize((x,y),Image.ANTIALIAS)
        return new_im

class Sprite(Base):
    def __init__(self,im='circle',xypos=(0.0,0.0),size=1,brightness=1.0,polar=False):
        super(Sprite,self).__init__()
        self._image_file = '{}/{}.png'.format(self.dfns.resource_path,im)
        self.size = size
        self.brightness = brightness
        self.image = ImageLoader(self._image_file,self.size,self.brightness)
        if polar:
            rho,deg=xypos
            theta=math.radians(deg)
            xypos=(rho*math.cos(theta), rho*math.sin(theta))
        self.pos=Point(*xypos)

    def draw(self,frame,center=None,mask=False):
        paste_im = self.image.image
        center = center or Point(0,0)
        new_pt=center+self.pos
        size=(self.size,self.size)
        #print self.size
        paste_pos = new_pt.pixels(size)
        #print paste_pos
        args=[paste_im,paste_pos]
        if mask:
            args.append(paste_im)
        #print args
        frame.image.paste(*args)
    
    def move(self,dPos):
        self.pos+=dPos

class Apeture(Sprite): # possible deprecated
    def __init__(self,apeture_im='circle',center=(0.0,0.0),
                        size=1,mask_color='black'):
        super(Apeture,self).__init__(apeture_im,center,size)
        # alpha <-> colors, then colors -> black

class CalibrationSquare(Sprite):
    def __init__(self,brightness=None,size=3,frame_no=0):
        pos=Point(*self.dfns.resolution)
        pos.scale(0.5)
        pad=2
        pos.set_pos(pos.x-pad,-pos.y+pad)
        lum=brightness or ((frame_no % 4)+2) / 5.0
        self.sq_base=Sprite(im='square',xypos=pos.pos,size=size,brightness=0)
        self.sq_diode=Sprite(im='square',xypos=pos.pos,
                        brightness=lum,size=size)

    def draw(self,frame,mask=False):
        self.sq_base.draw(frame,mask)
        self.sq_diode.draw(frame,mask)
        
class FixationDot(Sprite):
    def __init__(self,size=None):
        size=size or 0.25
        super(FixationDot,self).__init__(im='circle',xypos=(0.0,0.0),size=size)
        
class Record(Base):
    def __init__(self):
        super(Record,self).__init__()

class Point(Base):
    def __init__(self,x=0,y=0):
        self.set_pos(x,y)

    def __add__(u,v):
        new_pos = (u.x+v.x,u.y+v.y)
        return Point(*new_pos)

    def __neg__(u):
        new_pos = (-u.x,-u.y)
        return Point(new_pos)

    def __sub__(u,v): return u+(-v)

    def __abs__(u): return (u.x**2+u.y**2)**0.5

    def __mul__(u,v): return u.x*v.x + u.y*v.y
    
    def pt_wise_mul(u,v): return Point(u.x*v.x,u.y*v.y)

    def __imul__(u,v):
        raise TypeError('* returns scalar value, cannot be assigned to a Point')

    def __eq__(u,v): return u.x==v.x and u.y == v.y

    def __neq__(u,v): return not u==v

    def __mod__(u,v): return Point(u.x % v.x,u.y % v.y)

    def set_pos(self,x,y):
        self.x = x
        self.y = y
        self.pos = (self.x,self.y)

    def set_polar_pos(self,rho,theta):
        self.set_pos(rho*math.cos(theta),rho*math.sin(theta))

    def polar(self):
        rho=(self.x**2+self.y**2)**0.5
        theta=math.atan2(self.y,self.x)
        return rho,theta

    def scale(self,a):
        self.set_pos(a*self.x,a*self.y)

    def to_int(self,f): return int(round(f))

    def pixels(self,im_size):
        to_px = self.dfns.deg_to_px
        im_center = Point(*map(to_px,im_size))
        im_center.scale(-0.5)
        screen = Point(*self.dfns.resolution)
        #print im_center.pos, screen.pos, self.pos
        new_pos=Point(to_px(self.x),-to_px(self.y))+im_center+Point(0.5*screen.x,0.5*screen.y)
        new_pos=new_pos % screen
        #print new_pos.pos
        return tuple(map(self.to_int,new_pos.pos))

    def degrees(self):
        return self.pos


