import pygame
from car import *


class Process:
    Control_w = 0
    Control_a = 1
    Control_s = 2
    Control_d = 3
    Reset = 4
    Functional = 5

    def __init__(self, car: Car = None, surface: pygame.Surface = None):
        self.player = car
        self.surface = surface
        self.tracks = []
        self.control = [False, False, False, False, False, False]
        self.sensor = Sensor(self.player)

    def __update_control_k_d(self, e: pygame.event.Event):
        if e.key == pygame.K_w:
            self.control[Process.Control_w] = True
        elif e.key == pygame.K_a:
            self.control[Process.Control_a] = True
        elif e.key == pygame.K_s:
            self.control[Process.Control_s] = True
        elif e.key == pygame.K_d:
            self.control[Process.Control_d] = True
        elif e.key == pygame.K_r and not self.control[Process.Reset]:
            self.player.reset()
            self.control[Process.Reset] = True
        elif e.key == pygame.K_SPACE and not self.control[Process.Functional]:
            self.player.check_at_lane()
            self.sensor.print_info()
            self.control[Process.Functional] = True

    def __update_control_k_u(self, e: pygame.event.Event):
        if e.key == pygame.K_w:
            self.control[Process.Control_w] = False
        elif e.key == pygame.K_a:
            self.control[Process.Control_a] = False
        elif e.key == pygame.K_s:
            self.control[Process.Control_s] = False
        elif e.key == pygame.K_d:
            self.control[Process.Control_d] = False
        elif e.key == pygame.K_r:
            self.control[Process.Reset] = False
        elif e.key == pygame.K_SPACE:
            self.control[Process.Functional] = False

    # draw a car(rotated rectangle) by using pygame.draw.line 4 times
    # then draw the wheels
    def draw_car(self):
        draw_my_rect(self.surface, self.player.get_decision_points())
        self.draw_wheels()
        self.sensor.show_range(self.surface)

    # consider issue of screen coordinate system(c.hdg - c.turn)
    def draw_wheels(self):
        c = self.player
        x = c.x + c.length / 2 * cos(c.hdg) - c.width / 2 * sin(c.hdg)
        y = c.y + c.width / 2 * cos(c.hdg) + c.length / 2 * sin(c.hdg)
        draw_my_rect(self.surface, my_rect(x, y, c.length / 4, c.width / 3, c.hdg - c.turn))
        draw_my_rect(self.surface, my_rect(x + c.width * sin(c.hdg), y - c.width * cos(c.hdg),
                                           c.length / 4, c.width / 3, c.hdg - c.turn))

    def draw_track(self, t: Track):
        start_pos = t.lanes[0].area[Lane.REFERENCE].get_reference_pos()
        pygame.draw.circle(self.surface, "black", (start_pos[0], start_pos[1]), 5., 1)
        for lane in t.lanes:
            draw_lane(self.surface, lane)

    def update(self, framerate: float) -> bool:
        throttle = 0.
        turning = 0.
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return True
                self.__update_control_k_d(e)
            if e.type == pygame.KEYUP:
                self.__update_control_k_u(e)
        if self.control[Process.Control_w] and not self.player.collided:
            throttle = 1.
        # consider issue of screen coordinate system
        if self.control[Process.Control_a]:
            turning = 1.
            # turning = self.player.max_turning / framerate * pi
        if self.control[Process.Control_s]:
            throttle = -1.
        if self.control[Process.Control_d]:
            turning = -1.
            # turning = -self.player.max_turning / framerate * pi
        # return self.player.update(throttle, turning)
        self.player.update(throttle, turning)
        self.sensor.update_pos()
        return False


def get_rect(arc: Geometry) -> pygame.Rect:
    right_angle = pi / 2 if not arc.clockwise else -pi / 2
    a = turn(arc.hdg, right_angle)
    length = arc.length
    left = arc.x + length * (cos(a) - 1)
    top = arc.y + length * (sin(a) - 1)
    length *= 2
    return pygame.Rect(left, top, length, length)


def draw_my_rect(surface: pygame.surface,
                 ps: tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]):
    for i in range(4):
        pygame.draw.line(surface, 'black', ps[i], ps[(i + 1) % 4])


def draw_lane(surface: pygame.surface, lane: Lane):
    for side in (Lane.LEFT_SIDE, Lane.RIGHT_SIDE):
        geometry = lane.area[side]
        p = geometry.get_reference_pos(Geometry.START)
        x1 = p[0]
        y1 = p[1]
        a1 = -p[2]
        p = geometry.get_reference_pos(Geometry.END)
        x2 = p[0]
        y2 = p[1]
        a2 = -p[2]
        if geometry.lane_type is Geometry.LANE_TYPE_LINE:
            pygame.draw.line(surface, "black", (x1, y1), (x2, y2))
        else:
            right_angle = -pi / 2 if geometry.clockwise else pi / 2
            a1 = turn(a1, right_angle)
            a2 = turn(a2, right_angle)
            rect = get_rect(geometry)
            # temporary fix
            if geometry.clockwise:
                temp = a2
                a2 = a1
                a1 = temp
            pygame.draw.arc(surface, "black", rect, a2, a1)


class Sensor:
    def __init__(self, car: Car, sensor_range: float = 50, sensor_area: float = pi, sensor_count: int = 4):
        self.car = car
        self.sensor_range = sensor_range
        self.sensor_area = sensor_area
        self.sensor_count = sensor_count
        self.offset = self.car.length / 2
        self.x = None
        self.y = None
        self.dir = None
        self.update_pos()

    def update_pos(self):
        self.dir = self.car.hdg
        self.x = self.car.x + self.offset * cos(self.dir)
        self.y = self.car.y + self.offset * sin(self.dir)

    def show_range(self, surface: pygame.surface):
        d = turn(self.dir, -self.sensor_area / 2)
        da = self.sensor_area / self.sensor_count
        s_d: float
        for i in range(self.sensor_count + 1):
            s_d = self.car.get_distance(d)
            pygame.draw.line(surface, 'black', (self.x, self.y), get_end_point(self.x, self.y, d, s_d))
            d = turn(d, da)

    def print_info(self):
        d = turn(self.dir, -self.sensor_area / 2)
        da = self.sensor_area / self.sensor_count
        for i in range(self.sensor_count + 1):
            print('dir %d(%.2f deg) - %.3f' % (i, d / pi * 180, self.car.get_distance(d)))
            d = turn(d, da)
