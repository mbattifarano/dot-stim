from PIL import Image
import ReadStdIn
import sys
import operator as op
import math
import random as rand

PRM={}   # PARAMS is a global variable it should be READ ONLY except for 
            # when it is constructed from command line input

def main(arg_array):
    get_params(arg_array)
    return 0

def get_params(arg_array):
    global PRM # Allow get_params to modify the global variable
    PRM=ReadStdIn.parse(arg_array)
    PRM['px_per_cm']=map(op.div,PRM['resolution'],PRM['screen_size'])
    PRM['cm_per_px']=map(op.div,PRM['screen_size'],PRM['resolution'])
    PRM['deg_to_cm']=lambda deg : (PRM['dist_to_eye']*\
                                    math.tan(math.radians(deg)))
    PRM['cm_to_deg']=lambda cm : (math.degrees(\
                                    math.atan2(cm,PRM['dist_to_eye'])))
    PRM['field_limits']=deg_to_px(map(op.div,PRM['field_size'],(2.0,2.0)))
    print PRM
    return 0

def new_frame():
    MODE='L'
    SIZE=PRM['resolution']
    COLOR='black'
    return Image.new(MODE,SIZE,COLOR)

def save_frame(image,frame_no,base_name,path_to_file):
    filename='{}/{}/{:06d}.png'.format(path_to_file,base_name,frame_no)
    image.save(filename)
    return 0

def generate_dot_field(frame):
    paste_in_frame = lambda im : place_dot(frame,im)
    ndots=PRM['n_dots']
    DOTS=[get_dot() for i in range(ndots)]
    CENTER=get_dot((0,0))
    paste_in_frame(CENTER)
    map(paste_in_frame,DOTS)
    return 0
    
def place_dot(BG,dot):
    BG.paste(dot,pos_mask(dot.pos))
    return 0
    
def get_dot(xypos=None):
    dot=Image.open('ball.png')
    dot_size=deg_to_px(PRM['dot_size'])
    dot=dot.resize(dot_size,'ANTIALIAS')
    if xypos:
        pos=tuple(xypos)
    else:
        LB=map(op.mul,(-1,-1),PRM['field_limits'])
        UB=PRM['field_limits']
        step=2*dot_size
        pos=tuple(map(rand.randrange,LB,UB,(step,step)))
    dot.pos=pos # create pos attribute -- IN PIXELS
    return dot

def pos_mask(im):
# specify pixel coordinates with origin at center and translate to PIL
# coordinate system (origin top left)
    im_center=tuple(map(op.div,im.size,(-2.0,2.0)))
    pt=tuple(map(op.add,im.pos,im_center))
    offset=tuple(map(op.div,PRM['resolution'],(2.0,2.0)))
    pt_flip=map(op.mul,(1,-1),pt)
    return map(op.add,offset,pt_flip)

## conversion functions accept and return tuples (co-ordinates)

def cm_to_px(cm):
# returns cm co-ordinates (from center) in pixels
    return tuple(map(op.mul,cm,PRM['px_per_cm']))
    
def px_to_cm(px):
# returns pixel co-ordinates in cm from center of screen
    return tuple(map(op.mul,px,PRM['cm_per_px']))

def px_to_deg(px):
    cm=px_to_cm(px)
    deg=map(PRM['cm_to_deg'],cm)
    return tuple(deg)

def deg_to_px(deg):
    cm=map(PRM['deg_to_cm'],deg)
    px=cm_to_px(cm)
    return tuple(px)
    
if __name__ == '__main__':
    main(sys.argv[1:])
