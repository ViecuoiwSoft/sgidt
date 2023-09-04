import pygame
from car import *


class Process:
    def __init__(self, car: Car = None, surface: pygame.Surface = None):
        self.player = car
        self.surface = surface
        self.tracks = []

    def draw_car(self):
        ps = self.player.get_decision_points()
        pygame.draw.line(self.surface, "black", ps[0], ps[1])
        pygame.draw.line(self.surface, "black", ps[2], ps[3])
        pygame.draw.line(self.surface, "black", ps[0], ps[2])
        pygame.draw.line(self.surface, "black", ps[1], ps[3])

    def update(self) -> bool:
        throttle = 0.
        turning = 0.
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return True
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                throttle = 1.
                print("w pressed")
            if keys[pygame.K_a]:
                turning = self.player.max_turning / 360 * pi
                print("a pressed")
            if keys[pygame.K_d]:
                turning = -self.player.max_turning / 360 * pi
                print("d pressed")
        return self.player.update(throttle, turning)


def draw_track(t: Track, surface: pygame.Surface):
    start_pos = t.lanes[0].area[Lane.REFERENCE].get_reference_pos()
    pygame.draw.circle(surface, "black", (start_pos[0], start_pos[1]), 5., 1)
    for lane in t.lanes:
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
                pygame.draw.arc(surface, "black", rect, a2, a1)


def get_rect(arc: Geometry) -> pygame.Rect:
    right_angle = pi / 2 if not arc.clockwise else -pi / 2
    a = turn(arc.hdg, right_angle)
    length = arc.length
    left = arc.x + length * (cos(a) - 1)
    top = arc.y + length * (sin(a) - 1)
    length *= 2
    return pygame.Rect(left, top, length, length)


pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test Car")
screen.fill("white")
track1 = Track(None, 40.)
track1.generate_preset_1()
player = Car()
pos = track1.lanes[0].area[Lane.REFERENCE].get_reference_pos()
player.set(track1, *pos)
process1 = Process(player, screen)
draw_track(track1, screen)
collied = False
while not collied:
    collied = process1.update()
    process1.draw_car()
    pygame.display.flip()
print("collied!")
pygame.quit()
