from geometry import *
ERROR_CORRECTION = -10e-7


class Track:
    def __init__(self, lanes=None, width=0):
        self.lanes: list[Lane] = lanes
        self.width: int = width

    def get_spawn(self):
        if len(self.lanes) > 0:
            return self.lanes[0].area[Lane.REFERENCE].get_reference_pos()

    def append(self, lane_type: int, length: float, radian=0., clockwise=False, x=0., y=0., hdg=0.):
        if self.lanes is not None:
            reference = self.lanes[-1].area[Lane.REFERENCE]
            if lane_type == reference.lane_type and lane_type == Geometry.LANE_TYPE_LINE:
                return  # poka-yoke
            else:
                x, y, hdg = reference.get_reference_pos(Geometry.END)
        else:
            self.lanes = []
        self.lanes.append(Lane(self.width, Geometry(lane_type, x, y, hdg, length, radian, clockwise)))

    def random_generate(self):
        self.lanes = []
        pass

    def generate_preset_1(self):
        self.append(Geometry.LANE_TYPE_LINE, 400., 0., False, 200, 150)
        self.append(Geometry.LANE_TYPE_ARC, 150., pi)
        self.append(Geometry.LANE_TYPE_LINE, 400.)
        self.append(Geometry.LANE_TYPE_ARC, 150., pi)

    # 写的什么勾八赛道
    def generate_preset_2(self):
        self.append(Geometry.LANE_TYPE_LINE, 400., 0., False, 200, 150.)
        self.append(Geometry.LANE_TYPE_ARC, 40., pi, )
        self.append(Geometry.LANE_TYPE_ARC, 50., pi, True)
        self.append(Geometry.LANE_TYPE_ARC, 100., pi)
        self.append(Geometry.LANE_TYPE_LINE, 400.)
        self.append(Geometry.LANE_TYPE_ARC, 100., pi / 2)
        self.append(Geometry.LANE_TYPE_LINE, 180.)
        self.append(Geometry.LANE_TYPE_ARC, 100., pi / 2)

    def generate_preset_3(self):
        self.append(Geometry.LANE_TYPE_LINE, 400., 0., False, 200, 150.)
        self.append(Geometry.LANE_TYPE_ARC, 150., pi)
        self.append(Geometry.LANE_TYPE_LINE, 200.)
        self.append(Geometry.LANE_TYPE_ARC, 100., -pi / 2, True)
        self.append(Geometry.LANE_TYPE_LINE, 100.)
        self.append(Geometry.LANE_TYPE_ARC, 200., pi / 2)
        self.append(Geometry.LANE_TYPE_LINE, 150.)
        self.append(Geometry.LANE_TYPE_ARC, 150., pi)
        self.append(Geometry.LANE_TYPE_LINE, 200.)
        self.append(Geometry.LANE_TYPE_ARC, 300., pi / 2)
        self.append(Geometry.LANE_TYPE_LINE, 100.)
        self.append(Geometry.LANE_TYPE_ARC, 100., -pi / 2)
        self.append(Geometry.LANE_TYPE_LINE, 150.)

    def generate_preset_4(self):
        self.append(Geometry.LANE_TYPE_ARC, 50., pi, False, 200, 150.)
        self.append(Geometry.LANE_TYPE_ARC, 50., pi, True)
        self.append(Geometry.LANE_TYPE_ARC, 50., pi)
        self.append(Geometry.LANE_TYPE_ARC, 150., pi)


class Lane:
    REFERENCE = 0
    LEFT_SIDE = 1
    RIGHT_SIDE = 2

    def __init__(self, width: int, reference: Geometry):
        self.area: list[Geometry] = []
        self.width = width
        self.area.append(reference)
        self.area.append(reference.get_side(width, Geometry.LEFT))
        self.area.append(reference.get_side(width, Geometry.RIGHT))

    def at_lane(self, x: float, y: float) -> bool:
        res: bool
        g = self.area[Lane.REFERENCE]
        normal = g.hdg
        if g.lane_type is Geometry.LANE_TYPE_LINE:
            # res = abs(dot(v, vr)) <= lane.width / 2 and 0 <= dot(v, (cos(g.hdg), sin(g.hdg))) <= g.length
            pd = dot((x - g.x, y - g.y), (cos(g.hdg), sin(g.hdg)))
            res = ERROR_CORRECTION <= pd <= g.length  # using magic number instead of 0
        else:
            normal = turn(normal, -pi / 2) if g.clockwise else turn(normal, pi / 2)
            a = g.get_reference_pos(Geometry.END)[2]
            c_x = g.x - g.length * cos(normal)
            c_y = g.y - g.length * sin(normal)
            vr = (x - c_x, y - c_y)
            res = dot((cos(g.hdg), sin(g.hdg)), vr) >= 0 >= dot((cos(a), sin(a)), vr)
        res = res and self.area[Lane.LEFT_SIDE].at_right(x, y) and not self.area[Lane.RIGHT_SIDE].at_right(x, y)
        return res

    '''
    # circumstance of acute angle turning...
    def append(self, lane):
        if self.area[Lane.REFERENCE].hdg != lane.area[Lane.REFERENCE].hdg:
            pass
        pass
    '''
