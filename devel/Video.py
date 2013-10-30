from PIL import Image, ImageEnhance

class Trial(object): 
# Base class for all trial generator classes
    def __init__(self):
        # Namespace object returned by argparse
        self.params={'name_1':'value_1',
                     'name_2':'value_2'}
        self._resource_dir='resources'

class Video(Trial):
    def __init__(self):
        super(Video,self).__init__()
        self.frames=[]

    def write_frame(self,frame):
        pass

class Frame(Trial):
    def __init__(self):
        super(Frame,self).__init__()

class DotField(Trial):
    def __init__(self,center=(0.0,0.0),apeture_im='circle',size=5):
        super(DotField,self).__init__()
        self.center = center
        self._apeture_in = 'circle'
        self._apeture_size = size
        self.apeture = Apeture(apeture_im,center,size)

class Apeture(Sprite)
    def __init__(self,apeture_im='circle',center=(0.0,0.0),size=1)
        super(Apeture,self).__init__(apeture_im,center,size)
        # alpha <-> colors, then colors -> black

class ImageLoader(Trial):
    def __init__(self,im_file,size=1,brightness=1.0):
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
        w,h = im.size
        x = self.size / w
        y = self.size / h
        new_im = im.resize((x,y),Image.ANTIALIAS)
        return new_im

class Sprite(Trial):
    def __init__(self,im='circle',xypos=(0.0,0.0),size=1,brightness=1.0):
        super(Sprite,self).__init__()
        self._image_file = '{}/{}.png'.format(self._resource_dir,im)
        self.size = size
        self.brightness = brightness
        self.image = ImageLoader(self._image_file,self.size,self.brightness)
        self.x,self.y = xypos
        self.pos = (self.x,self.y)

    adjust_brightness = ImageLoader.adjust_brightness

    adjust_scale = ImageLoader.adjust_scale

class CalibrationSquare(Sprite):
    def __init__(self):
        super(CalibrationSquare,self).__init__()

class FixationDot(Sprite):
    def __init__(self):
        super(FixationDot,self).__init__()

class Render(Trial):
    def __init__(self):
        super(Render,self).__init__()

class Record(Trial):
    def __init__(self):
        super(Record,self).__init__()
    
