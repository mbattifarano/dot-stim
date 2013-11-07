import math
class Point(object):
    def __init__(self,x=0,y=0,convert=lambda x :x):
        self.set_pos(x,y)
        self.degrees=convert

    def __add__(u,v):
        new_pos = (u.x+v.x,u.y+v.y)
        return Point(*new_pos)

    def __neg__(u):
        new_pos = (-u.x,-u.y)
        return Point(new_pos)

    def __sub__(u,v): return u+(-v)

    def __abs__(u): return (u.x**2+u.y**2)**0.5

    def __mul__(u,v): return u.x*v.x + u.y*v.y

    def __imul__(u,v):
        raise TypeError('* returns scalar value, cannot be assigned to a Point')

    def __eq__(u,v): return u.x==v.x and u.y == v.y

    def __neq__(u,v): return not u==v

    def set_pos(self,x,y):
        self.x = int(round(x))
        self.y = int(round(y))
        self.pos = (self.x,self.y)

    def set_polar_pos(self,rho,theta):
        self.set_pos(rho*math.cos(theta),rho*math.sin(theta))

    def scale(self,a):
        self.set_pos(a*self.x,a*self.y)

    def pixels(self):
        return self.pos

