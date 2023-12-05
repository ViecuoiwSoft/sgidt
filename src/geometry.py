import sys
from math import sin, cos, pi, sqrt

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
        self.x: float = x  # coordinates indicate the
        self.y: float = y  # start of reference line
        self.hdg: float = hdg
        self.length: float = length  # when lane type is the arc this param indicates the radius
        self.radian: float = radian
        self.clockwise: bool = clockwise

    def get_center(self) -> tuple[float, float] | None:
        if self.lane_type == Geometry.LANE_TYPE_LINE:
            return
        na = turn(self.hdg, pi / 2 if self.clockwise else -pi / 2)
        return self.x - self.length * cos(na), self.y - self.length * sin(na)

    def get_reference_pos(self, percentage=0.) -> tuple[float, float, float]:
        if self.lane_type is Geometry.LANE_TYPE_LINE:
            x, y = get_end_point(self.x, self.y, self.hdg, self.length * percentage)
            return x, y, self.hdg
        else:
            return orbit(self.x, self.y, self.hdg, self.length, self.radian * percentage, self.clockwise)

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
    # def pass_through(self, x: float, y: float) -> bool:
    #     return (x - self.x) / cos(self.hdg) == (y - self.y) / sin(self.hdg)

    def at_right(self, x: float, y: float) -> bool:
        res: bool
        if self.lane_type is Geometry.LANE_TYPE_LINE:
            a = turn(self.hdg, pi / 2)
            pd = dot(((x - self.x), (y - self.y)), (cos(a), sin(a)))
            res = pd <= 0
        else:
            # how it should be dy - offset???
            # center of an arc have to calculate like this, bad
            # 2023.12.4 noted: also modified as dx - offset to test
            na = turn(self.hdg, pi / 2 if self.clockwise else -pi / 2)
            dx = self.x - self.length * cos(na) - x
            dy = self.y - self.length * sin(na) - y
            if self.clockwise:
                res = dx * dx + dy * dy <= self.length * self.length
            else:
                res = dx * dx + dy * dy >= self.length * self.length
            # print('(%.2f, %.2f) - (cx, cy): (dx = %.2f, dy = %.2f, r = %.2f)' % (x, y, dx, dy, g.length))
        return res

    def get_arc_angles(self) -> tuple[float, float] | None:
        if self.lane_type == Geometry.LANE_TYPE_LINE:
            return
        if self.clockwise:
            start = turn(self.hdg, pi / 2)
            end = turn(start, -self.radian)
        else:
            end = turn(self.hdg, -pi / 2)
            start = turn(end, self.radian)
        return start, end

    def get_distance_arc(self, x: float, y: float, hdg: float) -> float | None:
        cx, cy = self.get_center()  # center of an arc
        d = dot((cx - x, cy - y), (cos(hdg), sin(hdg)))  # may be negative, distance from (x, y) to the pedal
        x = x + d * cos(hdg)  # x of the pedal
        y = y + d * sin(hdg)  # y of the pedal
        vx = cx - x
        vy = cy - y
        m = vx * vx + vy * vy  # distance square from the pedal to the center
        if m > self.length * self.length:
            return
        m = sqrt(max(self.length * self.length - m, 0))  # assertion
        start, end = self.get_arc_angles()
        for dm in (-m, m):  # return the distance that shorter
            vx, vy = get_end_point(x, y, hdg, dm)  # choosing the reasonable distance based on the pedal
            vx -= self.x
            vy -= self.y
            # rotate (vx, vy) 90 deg, check if the intersection is on the arc
            if (dot((cos(end), sin(end)), (-vy, vx)) <= 0 <= dot((cos(start), sin(start)), (-vy, vx))) and d + dm > 0:
                return d + dm

    def get_distance_line(self, x: float, y: float, hdg: float) -> float | None:
        # may occur error
        if abs(dot((cos(self.hdg), sin(self.hdg)), (-sin(hdg), cos(hdg)))) < 10e-7:
            return
        l1, l2 = get_intersection_lambda(
            self.x, self.y, *get_end_point(self.x, self.y, self.hdg, self.length),
            x, y, *get_end_point(x, y, hdg))
        if 10e-7 <= l1 < 1:
            return l2

    def get_distance(self, x: float, y: float, hdg: float) -> float | None:
        if self.lane_type == Geometry.LANE_TYPE_LINE:
            return self.get_distance_line(x, y, hdg)
        else:
            return self.get_distance_arc(x, y, hdg)


def turn(hdg: float, angle: float) -> float:
    hdg += angle
    while hdg > pi * 2:
        hdg -= pi * 2
    while hdg < 0:
        hdg += pi * 2
    return hdg


def orbit(x: float, y: float, hdg: float, r: float, angle: float, clockwise=True) -> tuple[float, float, float]:
    right_angle = pi / 2
    if clockwise:
        angle = -angle
        right_angle = -right_angle
    x = x + r * (cos(turn(hdg, right_angle)) + cos(turn(hdg, angle - right_angle)))
    y = y + r * (sin(turn(hdg, right_angle)) + sin(turn(hdg, angle - right_angle)))
    hdg = turn(hdg, angle)
    return x, y, hdg


def my_rect(x: float, y: float, length: int, width: int, rot=0.):
    dx1 = length * cos(rot)
    dy1 = width * cos(rot)
    dx2 = width * sin(rot)
    dy2 = length * sin(rot)
    x = x - dx1 / 2 + dx2 / 2
    y = y - dy1 / 2 - dy2 / 2
    return (x, y), (x - dx2, y + dy1), \
        (x + dx1 - dx2, y + dy1 + dy2), (x + dx1, y + dy2)


def is_parallel(ax1: float, ay1: float, ax2: float, ay2: float,
                bx1: float, by1: float, bx2: float, by2: float) -> bool:
    # ay2 - ay1 / ax2 - ax1 = by2 - by1 / bx2 - bx1
    return (ay2 - ay1) * (bx2 - bx1) == (by2 - by1) * (ax2 - ax1)


# when you need some turning of acute angle rewrite this function
# ...for convenience we assume that every bend will be done by the arc

# the function will be used when one side of a lane does intersect
# with the side of another lane (not just 'link smoothly')

# however now we need to calculate the distance to the intersection
# of two lines :(
# when used this way check if lines are parallel before calling the function
# algorithm from https://zhuanlan.zhihu.com/p/363849472
def get_intersection_lambda(ax1: float, ay1: float, ax2: float, ay2: float,
                            bx1: float, by1: float, bx2: float, by2: float) -> tuple[float, float]:
    dx1 = ax2 - ax1
    dx2 = bx2 - bx1
    dy1 = ay2 - ay1
    dy2 = by2 - by1
    l1 = (bx1 * dy2 + ay1 * dx2 - by1 * dx2 - ax1 * dy2) / (dx1 * dy2 - dx2 * dy1)
    l2 = (ax1 * dy1 + by1 * dx1 - ay1 * dx1 - bx1 * dy1) / (dx2 * dy1 - dx1 * dy2)
    return l1, l2


# using parametric equation form of a segment
def get_end_point(x: float, y: float, a: float, length: float = 1) -> tuple[float, float]:
    return x + length * cos(a), y + length * sin(a)


def dot(v1: tuple[int | float, int | float], v2: tuple[int | float, int | float]) -> int | float:
    return v1[0] * v2[0] + v1[1] * v2[1]


if __name__ == '__main__':
    st1 = (0, 0)
    st2 = (200, 0)
    line1 = (*st1, *get_end_point(*st1, 0.25 * pi, 200))
    line2 = (*st2, *get_end_point(*st2, 0.75 * pi, 300))
    res1, res2 = get_intersection_lambda(*line1, *line2)
    print(line1, line2)
    s1, s2 = get_end_point(*st1, 0.25 * pi, 200 * res1), get_end_point(*st2, 0.75 * pi, 300 * res2)
    print('lambdas are: (%.2f, %.2f), two intersections are (%.2f, %.2f) and (%.2f, %.2f)' %
          (res1, res2, s1[0], s1[1], s2[0], s2[1]))
