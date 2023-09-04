from math import sin
from math import cos
from math import pi

"""
fuck screen coordinate system.
remember this:

 O--------------------> x
 |
 |
 |
 |
 |
 V y
"""


class Geometry:
    LANE_TYPE_LINE = 0
    LANE_TYPE_ARC = 1
    LEFT = False
    RIGHT = True
    START = 0
    END = 1

    def __init__(self, lane_type: int, x=0., y=0., hdg=0., length=0., radian=0., clockwise=False):
        self.lane_type: int = lane_type
        self.x: float = x
        self.y: float = y
        self.hdg: float = hdg
        self.length: float = length  # when lane type is the arc this param indicates the radius
        self.radian: float = radian
        self.clockwise: bool = clockwise

    def get_reference_pos(self, percentage=0.) -> tuple[float, float, float]:
        x = self.x
        y = self.y
        hdg = self.hdg
        if self.lane_type is Geometry.LANE_TYPE_LINE:
            x += self.length * percentage * cos(hdg)
            y += self.length * percentage * sin(hdg)
        else:
            angle = self.radian * percentage
            right_angle = pi / 2
            if self.clockwise:
                angle = -angle
                right_angle = -right_angle
            x = x + self.length * (
                    cos(turn(self.hdg, right_angle)) + cos(turn(self.hdg, angle - right_angle)))
            y = y + self.length * (
                    sin(turn(self.hdg, right_angle)) + sin(turn(self.hdg, angle - right_angle)))
            hdg = turn(hdg, angle)
        return x, y, hdg

    def get_side(self, width: int, side: int):
        width /= 2
        hdg = turn(self.hdg, pi / 2)
        if side is Geometry.LEFT:
            x = self.x + width * cos(hdg)
            y = self.y + width * sin(hdg)
        else:
            x = self.x - width * cos(hdg)
            y = self.y - width * sin(hdg)
        lane_type = self.lane_type
        length = self.length
        if lane_type is Geometry.LANE_TYPE_ARC:
            if (side is Geometry.LEFT and not self.clockwise) or (side is Geometry.RIGHT and self.clockwise):
                length -= width
            else:
                length += width
        radian = self.radian
        return Geometry(lane_type, x, y, self.hdg, length, radian, self.clockwise)

    # may occur error
    def pass_through(self, x: float, y: float) -> bool:
        return (x - self.x) / cos(self.hdg) == (y - self.y) / sin(self.hdg)

    '''
    # when you need some turning of acute angle rewrite this function
    # ...for convenience we assume that every bend will be done by the arc

    # the function will be used when one side of a lane does intersect
    # with the side of another lane (not just 'link smoothly')
    @staticmethod
    def get_intersection(f1, f2):
        pass
    '''


def turn(hdg: float, angle: float) -> float:
    hdg += angle
    if hdg > pi * 2:
        hdg -= pi * 2
    elif hdg < 0:
        hdg += pi * 2
    return hdg
