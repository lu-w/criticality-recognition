from owl_augmentator.owl_augmentator import augment, augment_class, AugmentationType
import owlready2
from .utils import *

import math
import numpy
from sympy import geometry
from shapely import wkt
from shapely.geometry import Point, Polygon, LineString

_INTERSECTING_PATH_THRESHOLD = 8   # s, the time interval in which future intersecting paths shall be detected
_INTERSECTING_PATH_MAX_PET = 3     # s, the time interval in which future intersecting paths shall be detected
_SPATIAL_PREDICATE_THRESHOLD = 50  # m, the distance in which spatial predicates are augmented
_IS_NEAR_DISTANCE = 4              # m, the distance for which spatial objects are close to each other
_IS_IN_PROXIMITY_DISTANCE = 15     # m, the distance for which spatial objects are in proximity to each other
_HIGH_REL_SPEED_THRESHOLD = 0.25   # rel., the relative difference in total speed in which CP 150 will be augmented
_DEFAULT_SPEED_LIMIT = 50          # km/h, the default speed limit that is assumed
_DEFAULT_MAX_SPEED = 50            # km/h, the default speed maximum speed that is assumed


def _lies_within_spatial_predicate_threshold(geo_self, geo_other):
    return float(geo_self.distance(geo_other)) <= _SPATIAL_PREDICATE_THRESHOLD


def register(physics: owlready2.Ontology):
    with physics:

        @augment_class
        class Dynamical_Object(owlready2.Thing):
            @augment(AugmentationType.REIFIED_DATA_PROPERTY, physics.Has_Distance_To, "distance_from", "distance_to",
                     "has_distance")
            def augment_distance(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    p1 = wkt.loads(self.hasGeometry[0].asWKT[0])
                    p2 = wkt.loads(other.hasGeometry[0].asWKT[0])
                    distance = float(p1.distance(p2))
                    if distance <= _SPATIAL_PREDICATE_THRESHOLD:
                        return distance

            @augment(AugmentationType.DATA_PROPERTY, "has_speed")
            def augment_speed(self):
                v = [x for x in [self.has_velocity_x, self.has_velocity_y, self.has_velocity_z] if x is not None]
                if len(v) > 1:
                    angle = math.degrees(math.atan2(v[1], v[0])) % 360
                    sign = 1
                    if 90 < angle < 270:
                        sign = -1
                    return float(sign * numpy.linalg.norm(v))

            @augment(AugmentationType.DATA_PROPERTY, "has_acceleration")
            def augment_acceleration(self):
                a = [x for x in [self.has_acceleration_x, self.has_acceleration_y, self.has_acceleration_z] if
                     x is not None]
                if len(a) > 1:
                    angle = math.degrees(math.atan2(a[1], a[0])) % 360
                    sign = 1
                    if 90 < angle < 270:
                        sign = -1
                    return float(sign * numpy.linalg.norm(a))

        @augment_class
        class Moving_Dynamical_Object(owlready2.Thing):
            @augment(AugmentationType.OBJECT_PROPERTY, "has_intersecting_path")
            def augment_has_intersecting_path(self, other: physics.Moving_Dynamical_Object):
                # TODO document in OWL
                if same_scene(self, other) and has_geometry(self) and has_geometry(other) and self.has_yaw is not None \
                        and other.has_yaw is not None and self.has_speed and other.has_speed:
                    p_1 = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                    p_2 = wkt.loads(other.hasGeometry[0].asWKT[0]).centroid
                    p_self = geometry.Point(p_1.x, p_1.y)
                    p_other = geometry.Point(p_2.x, p_2.y)
                    if p_self != p_other:
                        self_yaw = self.has_yaw
                        other_yaw = other.has_yaw
                        if self.has_speed < 0:
                            self_yaw = (self.has_yaw + 180) % 360
                        if other.has_speed < 0:
                            other_yaw = (other.has_yaw + 180) % 360
                        p_self_1 = geometry.Point(p_1.x + math.cos(math.radians(self_yaw)),
                                                  p_1.y + math.sin(math.radians(self_yaw)))
                        p_other_1 = geometry.Point(p_2.x + math.cos(math.radians(other_yaw)),
                                                   p_2.y + math.sin(math.radians(other_yaw)))
                        self_path = geometry.Ray(p_self, p_self_1)
                        other_path = geometry.Ray(p_other, p_other_1)
                        p_cross = geometry.intersection(self_path, other_path)
                        if len(p_cross) > 0:
                            d_self = geometry.Point.distance(p_cross[0], p_self)
                            d_other = geometry.Point.distance(p_cross[0], p_other)
                            t_self = float(d_self) / self.has_speed
                            t_other = float(d_other) / other.has_speed
                            return t_self + t_other < _INTERSECTING_PATH_THRESHOLD and \
                                   abs(t_self - t_other) < _INTERSECTING_PATH_MAX_PET
                        else:
                            return False

            @augment(AugmentationType.OBJECT_PROPERTY, "CP_163")
            def augment_cp_163(self, other: physics.Moving_Dynamical_Object):
                # High relative speed
                if self != other and same_scene(self, other) and has_geometry(self) and has_geometry(other) and \
                        self.has_yaw is not None and other.has_yaw is not None and self.has_velocity_x is not None and \
                        self.has_velocity_y is not None and other.has_velocity_x is not None and other.has_velocity_x \
                        is not None:
                    # TODO document in OWL
                    v_self = numpy.array(
                        convert_local_to_global_vector([self.has_velocity_x, self.has_velocity_y], self.has_yaw))
                    v_other = numpy.array(
                        convert_local_to_global_vector([other.has_velocity_x, other.has_velocity_y], other.has_yaw))
                    s_rel = numpy.linalg.norm(v_self - v_other)
                    s_self_max = max([x for y in self.is_a for x in y.has_maximum_speed])
                    if s_self_max is not None:
                        s_self_max = _DEFAULT_MAX_SPEED
                    if self.has_speed_limit is not None:
                        s_rule_max = self.has_speed_limit
                    elif len(self.in_traffic_model) > 0 and self.in_traffic_model[0].has_speed_limit is not None:
                        s_rule_max = self.in_traffic_model[0].has_speed_limit
                    else:
                        s_rule_max = _DEFAULT_SPEED_LIMIT
                    s_rel_normed = s_rel / (min(s_self_max, s_rule_max))
                    return s_rel_normed >= _HIGH_REL_SPEED_THRESHOLD

        @augment_class
        class Spatial_Object(owlready2.Thing):
            @augment(AugmentationType.OBJECT_PROPERTY, "is_in_proximity")
            def augment_is_in_proximity(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    p1 = wkt.loads(self.hasGeometry[0].asWKT[0])
                    p2 = wkt.loads(other.hasGeometry[0].asWKT[0])
                    if float(p1.distance(p2)) < _IS_IN_PROXIMITY_DISTANCE:
                        return True

            @augment(AugmentationType.OBJECT_PROPERTY, "is_near")
            def augment_is_near(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    p1 = wkt.loads(self.hasGeometry[0].asWKT[0])
                    p2 = wkt.loads(other.hasGeometry[0].asWKT[0])
                    if float(p1.distance(p2)) < _IS_NEAR_DISTANCE:
                        return True

            @augment(AugmentationType.OBJECT_PROPERTY, "sfIntersects")
            def augment_intersects(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.intersects(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "sfOverlaps")
            def augment_overlaps(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.overlaps(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "sfTouches")
            def augment_touches(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.touches(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "sfWithin")
            def augment_within(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.within(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "sfDisjoint")
            def augment_disjoint(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    if _lies_within_spatial_predicate_threshold(geo_self, geo_other):
                        return geo_self.disjoint(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "sfCrosses")
            def augment_crosses(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.crosses(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "sfContains")
            def augment_contains(self, other: physics.Spatial_Object):
                if same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    geo_self = wkt.loads(self.hasGeometry[0].asWKT[0])
                    geo_other = wkt.loads(other.hasGeometry[0].asWKT[0])
                    return geo_self.contains(geo_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "is_behind")
            def augment_is_behind(self, other: physics.Dynamical_Object):
                if same_scene(self, other) and self != other and has_geometry(self) and has_geometry(other) and \
                        other.has_yaw is not None:
                    p_1 = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                    p_2 = wkt.loads(other.hasGeometry[0].asWKT[0]).centroid
                    if _lies_within_spatial_predicate_threshold(p_1, p_2) and not (math.isclose(p_1.x, p_2.x) and
                                                                                   math.isclose(p_1.y, p_2.y)):
                        p_yaw = [math.cos(math.radians(other.has_yaw)), math.sin(math.radians(other.has_yaw))]
                        p_self = [p_1.x - p_2.x, p_1.y - p_2.y]
                        angle = math.degrees(math.atan2(*p_yaw) - math.atan2(*p_self)) % 360
                        return 90 < angle < 270

            @augment(AugmentationType.OBJECT_PROPERTY, "is_left_of")
            def augment_is_left_of(self, other: physics.Dynamical_Object):
                if same_scene(self, other) and self != other and has_geometry(self) and has_geometry(other) and \
                        other.has_yaw is not None:
                    p_1 = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                    p_2 = wkt.loads(other.hasGeometry[0].asWKT[0]).centroid
                    if _lies_within_spatial_predicate_threshold(p_1, p_2) and not (math.isclose(p_1.x, p_2.x) and
                                                                                   math.isclose(p_1.y, p_2.y)):
                        p_yaw = [math.cos(math.radians(other.has_yaw)), math.sin(math.radians(other.has_yaw))]
                        p_self = [p_1.x - p_2.x, p_1.y - p_2.y]
                        angle = math.degrees(math.atan2(*p_yaw) - math.atan2(*p_self)) % 360
                        return 0 < angle < 180

            @augment(AugmentationType.OBJECT_PROPERTY, "is_right_of")
            def augment_is_right_of(self, other: physics.Dynamical_Object):
                if same_scene(self, other) and self != other and has_geometry(self) and has_geometry(other) and \
                        other.has_yaw is not None:
                    p_1 = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                    p_2 = wkt.loads(other.hasGeometry[0].asWKT[0]).centroid
                    if _lies_within_spatial_predicate_threshold(p_1, p_2) and not (math.isclose(p_1.x, p_2.x) and
                                                                                   math.isclose(p_1.y, p_2.y)):
                        p_yaw = [math.cos(math.radians(other.has_yaw)), math.sin(math.radians(other.has_yaw))]
                        p_self = [p_1.x - p_2.x, p_1.y - p_2.y]
                        angle = math.degrees(math.atan2(*p_yaw) - math.atan2(*p_self)) % 360
                        return 180 < angle < 360

            @augment(AugmentationType.OBJECT_PROPERTY, "is_in_front_of")
            def augment_is_in_front_of(self, other: physics.Dynamical_Object):
                if same_scene(self, other) and self != other and has_geometry(self) and has_geometry(other) and \
                        other.has_yaw is not None:
                    p_1 = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                    p_2 = wkt.loads(other.hasGeometry[0].asWKT[0]).centroid
                    if _lies_within_spatial_predicate_threshold(p_1, p_2) and not (math.isclose(p_1.x, p_2.x) and
                                                                                   math.isclose(p_1.y, p_2.y)):
                        p_yaw = [math.cos(math.radians(other.has_yaw)), math.sin(math.radians(other.has_yaw))]
                        p_self = [p_1.x - p_2.x, p_1.y - p_2.y]
                        angle = math.degrees(math.atan2(*p_yaw) - math.atan2(*p_self)) % 360
                        return angle < 90 or angle > 270
