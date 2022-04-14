import numpy
from owl_augmentator.owl_augmentator import augment, augment_class, concepts, AugmentationType
import owlready2
from shapely import wkt
from shapely.geometry import Polygon
from matplotlib import pyplot as plt
import matplotlib

from .utils import *

_MAX_TIME_SMALL_DISTANCE = 1  # s, the time in which distances are considered to be 'small'


def _rec_ids(i):
    ids = {i}
    change = True
    while change:
        update = ids.union(set([y for x in ids for y in x.identical_to]))
        if len(update) == len(ids):
            change = False
        else:
            ids = update
    return ids


def register(l4_core: owlready2.Ontology, l4_de: owlready2.Ontology, l2_de: owlready2.Ontology,
             physics: owlready2.Ontology, time: owlready2.Ontology):
    def get_relevant_area(thing: owlready2.Thing) -> Polygon:
        """
        Helper function for CP small distance. Dispatches to subclass helper functions.
        """
        geom = wkt.loads(thing.hasGeometry[0].asWKT[0]).buffer(0)
        if thing.has_speed is not None:
            speed = thing.has_speed
        else:
            speed = 0
        if thing.has_yaw is not None:
            yaw = thing.has_yaw
        else:
            yaw = 0
        if l4_core.Vehicle in thing.INDIRECT_is_a and speed > 0:
            max_yaws = [x for y in thing.is_a for x in y.has_maximum_yaw]
            max_yaw_rates = [x for y in thing.is_a for x in y.has_maximum_yaw_rate]
            if len(max_yaws) > 0:
                max_yaw = max(max_yaws)
            else:
                max_yaw = 45
            if len(max_yaw_rates) > 0:
                max_yaw_rate = max(max_yaw_rates)
            else:
                max_yaw_rate = 25
            return get_relevant_area_veh(geom, speed, yaw, max_yaw_rate, max_yaw)
        elif l4_core.Pedestrian in thing.INDIRECT_is_a:
            return get_relevant_area_ped(geom, speed)
        else:
            return geom

    def get_relevant_area_ped(a: Polygon, speed: float) -> Polygon:
        """
        Helper function for CP small distance for pedestrians. Gets the relevant area of a pedestrian as a Polygon.
        """
        if speed > 0:
            return a.centroid.buffer(_MAX_TIME_SMALL_DISTANCE * speed + math.sqrt(a.area))
        else:
            return a

    def get_relevant_area_veh(a: Polygon, speed: float, yaw: float, max_yaw_rate: float, max_yaw: float = 20) -> \
            Polygon:
        """
        Helper function for CP small distance for vehicles. Gets the relevant area of a vehicle as a Polygon.
        """

        def pos(a_pos: tuple, speed_pos: float, yaw_pos: float, max_yaw_rate_pos: float, max_yaw_pos: float,
                t_pos: float) \
                -> tuple:
            """
            Simple prediction model. Calculates the 2D-point at which the actor will be  at time t + t_pos assuming the
            given parameters.
            """
            if abs(max_yaw_rate_pos * t_pos) <= max_yaw_pos:
                theta = (yaw_pos + (max_yaw_rate_pos * (t_pos ** 2)) / 2) % 360
            else:
                theta = (yaw_pos + (
                        -(max_yaw_pos ** 2) / (2 * max_yaw_rate_pos) + numpy.sign(max_yaw_rate_pos) * max_yaw *
                        t_pos)) % 360
            return speed_pos * t_pos * math.cos(math.radians(theta)) + a_pos[0], \
                   speed_pos * t_pos * math.sin(math.radians(theta)) + a_pos[1]

        yaw_sampling = 1
        samples = []
        for cur_max_yaw_rate in numpy.arange(-max_yaw_rate, max_yaw_rate + yaw_sampling, yaw_sampling):
            path = []
            if cur_max_yaw_rate < 0:
                a_point = left_front_point(a, yaw)
            else:
                a_point = right_front_point(a, yaw)
            if abs(cur_max_yaw_rate) == max_yaw_rate:
                for t in numpy.arange(0, _MAX_TIME_SMALL_DISTANCE + 0.2, 0.2):
                    path.append(pos(a_point, speed, yaw, cur_max_yaw_rate, max_yaw, t))
            else:
                path.append(pos(a_point, speed, yaw, cur_max_yaw_rate, max_yaw, _MAX_TIME_SMALL_DISTANCE))
            samples.append(path)
        geo = Polygon(samples[0] + [x[-1] for x in samples] + list(reversed(samples[-1])))
        return geo.union(a)

    with l4_core:

        @augment_class
        class Pedestrian(owlready2.Thing):
            @augment(AugmentationType.OBJECT_PROPERTY, "CP_150")
            def augment_cp_150(self, other: physics.Spatial_Object):
                # Small distance
                if self != other and same_scene(self, other) and has_geometry(self) and has_geometry(other) and \
                        self.has_speed is not None and other.has_height is not None and other.has_height > 0:
                    # TODO document in OWL
                    occ1 = get_relevant_area(self)
                    occ2 = get_relevant_area(other)
                    return occ1.intersects(occ2)

        @augment_class
        class Vehicle(owlready2.Thing):
            @augment(AugmentationType.OBJECT_PROPERTY, "CP_150")
            def augment_cp_150(self, other: physics.Spatial_Object):
                # Small distance
                if self != other and same_scene(self, other) and has_geometry(self) and has_geometry(other) and \
                        self.has_speed is not None and self.has_yaw is not None and other.has_height is not None and \
                        other.has_height > 0:
                    # TODO document in OWL
                    occ1 = get_relevant_area(self)
                    occ2 = get_relevant_area(other)
                    return occ1.intersects(occ2)

        @augment_class
        class Driver(owlready2.Thing):
            @augment(AugmentationType.REIFIED_OBJECT_PROPERTY, l4_de.Pass,
                     ["conducted_by", "has_participant", "hasBeginning", "hasEnd", "belongs_to"])
            @concepts(l4_core.Driver, physics.Spatial_Object, time.TimePosition)
            def augment_pass(self, other: l4_core.L4_Entity):
                if physics.Spatial_Object in other.INDIRECT_is_a and len(self.drives) > 0:
                    passes = False
                    scene_1 = None
                    scene_2 = self.in_traffic_model[0]
                    scenario = None
                    if len(scene_2.belongs_to) > 0 and len(self.drives) > 0:
                        scenario = scene_2.belongs_to[0]
                        self_veh = self.drives[0]
                        if self_veh in other.is_behind and self_veh in other.is_in_proximity:
                            self_veh_ids = [x for x in _rec_ids(self_veh) if len(x.in_traffic_model) > 0 and
                                            len(x.in_traffic_model[0].inTimePosition) > 0 and
                                            len(x.in_traffic_model[0].inTimePosition[0].numericPosition) > 0]
                            other_ids = [x for x in _rec_ids(other) if len(x.in_traffic_model) > 0 and
                                         len(x.in_traffic_model[0].inTimePosition) > 0 and
                                         len(x.in_traffic_model[0].inTimePosition[0].numericPosition) > 0]
                            self_veh_time_slices = sorted(filter(lambda x: x.in_traffic_model[0].inTimePosition[0].
                                                                 numericPosition[0] <= self_veh.in_traffic_model[0].
                                                                 inTimePosition[0].numericPosition[0],
                                                                 self_veh_ids),
                                                          key=lambda x: -x.in_traffic_model[0].inTimePosition[0].
                                                          numericPosition[0])
                            other_time_slices = sorted(filter(lambda x: x.in_traffic_model[0].inTimePosition[0].
                                                              numericPosition[0] <= other.in_traffic_model[0].
                                                              inTimePosition[0].numericPosition[0],
                                                              other_ids),
                                                       key=lambda x: -x.in_traffic_model[0].inTimePosition[0].
                                                       numericPosition[0])
                            time_slices = []
                            for s_ts in self_veh_time_slices[1:]:
                                for o_ts in other_time_slices[1:]:
                                    if s_ts.in_traffic_model[0] == o_ts.in_traffic_model[0]:
                                        time_slices.append((s_ts, o_ts))
                            if len(time_slices) > 0 and time_slices[-1][0] not in time_slices[-1][1].is_behind:
                                for t in time_slices:
                                    # if t[0] not in t[1].is_in_proximity: break
                                    if t[0] in t[1].is_in_front_of and t[0] in t[1].is_in_proximity:
                                        passes = True
                                        scene_1 = t[0].in_traffic_model[0]
                                        break
                    return passes, scene_1, scene_2, scenario
