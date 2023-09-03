from track import *

"""
踩下油门->汽车加速
汽车匀速->加速度克服风阻
"""


class Car:
    def __init__(self, length=20, width=12, max_speed=20., max_acceleration=5., max_turning=35.):
        self.length = length
        self.width = width
        self.track = None
        self.x = 0.
        self.y = 0.
        self.hdg = 0.
        self.speed = 0.
        self.acceleration = 0.
        self.throttle = 0.  # 'acceleration percentage'
        self.collided = False
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration
        self.max_turning = max_turning

    def set(self, track: Track = None, x=0., y=0., hdg=0., acceleration=0., speed=0., throttle=0., collided=False):
        self.track = track
        self.x = x
        self.y = y
        self.hdg = hdg
        self.acceleration = acceleration
        self.speed = speed
        self.throttle = throttle
        self.collided = collided

    def update(self, throttle=0., turning=0.) -> bool:
        self.throttle = throttle
        self.__update_acceleration()
        self.speed = min(self.max_speed, self.speed + self.acceleration)
        self.hdg = turn(self.hdg, turning)
        self.__update_pos()
        self.__handle_collision()
        return self.collided

    def __update_acceleration(self):
        k = 1.
        drag = k * self.speed * self.speed  # F = k * v^2
        self.acceleration = self.max_acceleration * self.throttle - drag  # may not rigorous

    def __update_pos(self):
        self.x += self.speed * cos(self.hdg)
        self.y += self.speed * sin(self.hdg)

    def __handle_collision(self):
        p_at_lane = 0
        for p in self.get_decision_points():
            for lane in self.track.lanes:
                if at_lane(p[0], p[1], lane):
                    p_at_lane += 1
        self.collided = p_at_lane < 4

    def get_decision_points(self):
        v = turn(self.hdg, pi / 2)
        dx1 = self.length * cos(self.hdg) / 2
        dy1 = self.length * sin(self.hdg) / 2
        dx2 = self.width * cos(v) / 2
        dy2 = self.width * sin(v) / 2

        return (self.x + dx1 + dx2, self.y + dy1 + dy2), (self.x + dx1 - dx2, self.y + dy1 - dy2), \
            (self.x - dx1 + dx2, self.y - dy1 + dy2), (self.x - dx1 - dx2, self.y - dy1 - dy2)


def at_lane(x: float, y: float, lane: Lane) -> bool:
    res: bool
    g = lane.area[Lane.REFERENCE]
    pos = g.get_reference_pos(Geometry.END)
    if g.lane_type is Geometry.LANE_TYPE_LINE:
        vr = (cos(g.hdg), sin(g.hdg))
        v1 = (x - g.x, y - g.y)
        v2 = (x - pos[0], y - pos[1])
        res = dot(v1, vr) >= 0 >= dot(v2, vr)
    else:
        if g.clockwise:
            vr = (x - g.x - g.length * cos(turn(g.hdg, -pi / 2)), y - g.y - g.length * sin(turn(g.hdg, -pi / 2)))
        else:
            vr = (x - g.x - g.length * cos(turn(g.hdg, pi / 2)), y - g.y - g.length * sin(turn(g.hdg, pi / 2)))
        res = dot((cos(g.hdg), sin(g.hdg)), vr) >= 0 >= dot((cos(pos[2]), sin(pos[2])), vr)
        res = res and at_right(x, y, lane.area[Lane.LEFT_SIDE]) and not at_right(x, y, lane.area[Lane.RIGHT_SIDE])
    return res


def at_right(x: float, y: float, g: Geometry) -> bool:
    res: bool
    if g.lane_type is Geometry.LANE_TYPE_LINE:
        a = turn(g.hdg, pi / 2)
        res = dot(((x - g.x), (y - g.x)), (cos(a), sin(a))) >= 0
    else:
        dx = g.x
        dy = g.y
        if g.clockwise:
            dx = dx + g.length * cos(turn(g.hdg, pi / 2)) - x
            dy = dy + g.length * sin(turn(g.hdg, pi / 2)) - y
            res = dx * dx + dy * dy <= g.length * g.length
        else:
            dx = dx + g.length * cos(turn(g.hdg, -pi / 2)) - x
            dy = dy + g.length * sin(turn(g.hdg, -pi / 2)) - y
            res = dx * dx + dy * dy >= g.length * g.length
    return res


def dot(v1: tuple[int | float, int | float], v2: tuple[int | float, int | float]) -> int | float:
    return v1[0] * v2[0] + v1[1] * v2[1]
