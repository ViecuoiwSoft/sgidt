from track import *

"""
踩下油门->汽车加速
汽车匀速->加速度克服风阻
"""

# used in collision handling
# when a car slowly passing through the connection part of two lanes
# using 0 in calculation may occur 'fake collision', maybe it's the reason
# I just being lazy to find out the true reason of this problem(maybe the matter of bad algorithm)
# so use this magic number instead, just a very small negative number
ERROR_CORRECTION = -10e-7
TIME_QUANTITY = 60


class Car:
    def __init__(self, length=20, width=12, max_speed=5., max_acceleration=2., max_turning=0.25):
        self.length = length
        self.width = width
        self.track = None
        self.x = 0.
        self.y = 0.
        self.hdg = 0.
        self.speed = 0.
        self.acceleration = 0.
        self.turn = 0
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

    def update(self, throttle, turning) -> bool:
        self.throttle = throttle
        self.__update_acceleration()
        self.speed = max(min(self.max_speed, self.speed + self.acceleration), 0)
        self.__update_turning(turning)
        self.__update_pos()
        self.__handle_collision()
        return self.collided

    def __update_turning(self, turning: float):
        self.turn = turning * self.max_turning
        # if turning == 0 and self.turn != 0:
        #     self.turn = 0
        # elif abs(self.turn) < self.max_turning:
        #     if turning > 0:
        #         self.turn = min(self.max_turning, self.turn + turning)
        #     else:
        #         self.turn = max(-self.max_turning, self.turn + turning)

    def __update_acceleration(self):
        self.acceleration = self.throttle * self.max_acceleration / TIME_QUANTITY
        if self.throttle == 0 and self.speed > 0:
            self.acceleration = -self.max_acceleration / TIME_QUANTITY * 5
        # k = 0.3  # drag coefficient
        # drag = k * self.speed * self.speed  # F = k * v^2
        # self.acceleration = self.max_acceleration * self.throttle - drag  # may not rigorous

    def __update_pos(self):
        if self.turn == 0.:
            self.x += self.speed * cos(self.hdg)
            self.y += self.speed * sin(self.hdg)
        elif self.speed != 0:
            r = self.length / (2 * sin(self.turn))  # turning radius
            clockwise = r > 0
            if not clockwise:
                r = -r
            a = self.speed / (2 * r) * pi  # linear speed to angular speed
            self.x, self.y, self.hdg = orbit(self.x, self.y, self.hdg, r, a, clockwise)

    def __handle_collision(self):
        p_at_lane = 0
        for lane in self.track.lanes:
            for p in self.get_decision_points():
                if at_lane(p[0], p[1], lane):
                    p_at_lane += 1
        self.collided = p_at_lane < 4

    def get_decision_points(self):
        return my_rect(self.x, self.y, self.length, self.width, self.hdg)

    def check_at_lane(self):
        ps = self.get_decision_points()
        ns = ('LB', 'RB', 'RF', 'LF')
        for i in range(4):
            print('%s: (%f, %f)' % (ns[i], ps[i][0], ps[i][1]))
        for j in range(len(self.track.lanes)):
            for i in range(4):
                if not at_lane(*ps[i], self.track.lanes[j]):
                    print('%s is not at lane %d' % (ns[i], j))
                else:
                    print('%s is at lane %d' % (ns[i], j))

    def reset(self):
        if self.track is not None:
            self.set(self.track, *self.track.lanes[0].area[Lane.REFERENCE].get_reference_pos())


def at_lane(x: float, y: float, lane: Lane) -> bool:
    res: bool
    g = lane.area[Lane.REFERENCE]
    normal = g.hdg
    pos = g.get_reference_pos(Geometry.END)
    if g.lane_type is Geometry.LANE_TYPE_LINE:
        # res = abs(dot(v, vr)) <= lane.width / 2 and 0 <= dot(v, (cos(g.hdg), sin(g.hdg))) <= g.length
        pd = dot((x - g.x, y - g.y), (cos(g.hdg), sin(g.hdg)))
        res = ERROR_CORRECTION <= pd <= g.length  # using magic number instead of 0
    else:
        normal = turn(normal, -pi / 2) if g.clockwise else turn(normal, pi / 2)
        c_x = g.x - g.length * cos(normal)
        c_y = g.y - g.length * sin(normal)
        vr = (x - c_x, y - c_y)
        res = dot((cos(g.hdg), sin(g.hdg)), vr) >= 0 >= dot((cos(pos[2]), sin(pos[2])), vr)
    res = res and at_right(x, y, lane.area[Lane.LEFT_SIDE]) and not at_right(x, y, lane.area[Lane.RIGHT_SIDE])
    return res


def at_right(x: float, y: float, g: Geometry) -> bool:
    res: bool
    if g.lane_type is Geometry.LANE_TYPE_LINE:
        a = turn(g.hdg, pi / 2)
        pd = dot(((x - g.x), (y - g.y)), (cos(a), sin(a)))
        res = pd <= 0
    else:
        dx = g.x
        dy = g.y
        # how it should be dy - offset???
        # center of an arc have to calculate like this, bad
        if g.clockwise:
            dx = dx + g.length * cos(turn(g.hdg, pi / 2)) - x
            dy = dy - g.length * sin(turn(g.hdg, pi / 2)) - y
            res = dx * dx + dy * dy <= g.length * g.length
        else:
            dx = dx + g.length * cos(turn(g.hdg, -pi / 2)) - x
            dy = dy - g.length * sin(turn(g.hdg, -pi / 2)) - y
            res = dx * dx + dy * dy >= g.length * g.length
        # print('(%.2f, %.2f) - (%.2f, %.2f): (dx = %.2f, dy = %.2f, r = %.2f)' % (x, y, cx, cy, dx, dy, g.length))
    return res


def dot(v1: tuple[int | float, int | float], v2: tuple[int | float, int | float]) -> int | float:
    return v1[0] * v2[0] + v1[1] * v2[1]
