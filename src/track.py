from geometry import *


class Track:
    def __init__(self, lanes=None, width=0):
        self.lanes: list[Lane] = lanes
        self.width: int = width

    def get_spawn(self):
        if len(self.lanes) > 0:
            return self.lanes[0].area[Lane.REFERENCE].get_reference_pos()

    def append(self, lane_type, length: float, radian=0., clockwise=False, x=0., y=0., hdg=0.):
        if self.lanes is not None:
            reference = self.lanes[-1].area[Lane.REFERENCE]
            if (lane_type is reference.lane_type) and (lane_type is Geometry.LANE_TYPE_LINE):
                return
            else:
                end_pos = reference.get_reference_pos(Geometry.END)
                x = end_pos[0]
                y = end_pos[1]
                hdg = end_pos[2]
        else:
            self.lanes = []
        new_reference = Geometry(lane_type, x, y, hdg, length, radian, clockwise)
        self.lanes.append(Lane(self.width, new_reference))

    def random_generate(self):
        self.lanes = []
        pass

    def generate_preset_1(self):
        self.append(Geometry.LANE_TYPE_LINE, 400., 0., False, 400, 300.)
        self.append(Geometry.LANE_TYPE_ARC, 100., pi)
        self.append(Geometry.LANE_TYPE_LINE, 400.)
        self.append(Geometry.LANE_TYPE_ARC, 100., pi)


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

    '''
    # circumstance of acute angle turning...
    def append(self, lane):
        if self.area[Lane.REFERENCE].hdg != lane.area[Lane.REFERENCE].hdg:
            pass
        pass
    '''
