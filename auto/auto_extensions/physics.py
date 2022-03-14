from owl_augmentator.owl_augmentator import augment, augment_class, AugmentationType
import owlready2
from .utils import *

import math
import numpy
from sympy import geometry
from shapely import wkt
from shapely.geometry import Point, Polygon, LineString

# TODO make this threshold speed dependent and not an absolute distance
_INTERSECTING_PATH_THRESHOLD = 10  # s, the time interval in which future intersecting paths shall be detected
_SPATIAL_PREDICATE_THRESHOLD = 50  # m, the distance in which spatial predicates are augmented
_IS_NEAR_DISTANCE = 2              # m, the distance for which spatial objects are close to each other
_IS_IN_PROXIMITY_DISTANCE = 15     # m, the distance for which spatial objects are in proximity to each other
# TODO maybe this threshold can be chosen based on situation (e.g. bicyclist vs vehicle, crossing vs. parallel, ...)
_HIGH_REL_SPEED_THRESHOLD = 0.25   # rel., the relative difference in total speed in which CP 150 will be augmented


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
                    sign = 1
                    if self.has_yaw is not None:
                        if numpy.dot((math.cos(math.radians(self.has_yaw)), math.sin(math.radians(self.has_yaw))),
                                     v[:2]) < 0:
                            sign = -1
                    return float(sign * numpy.linalg.norm(v))

            @augment(AugmentationType.DATA_PROPERTY, "has_acceleration")
            def augment_acceleration(self):
                a = [x for x in [self.has_acceleration_x, self.has_acceleration_y, self.has_acceleration_z] if
                     x is not None]
                if len(a) > 1:
                    sign = 1
                    if self.has_yaw is not None:
                        if numpy.dot((math.cos(math.radians(self.has_yaw)), math.sin(math.radians(self.has_yaw))),
                                     a[:2]) < 0:
                            sign = -1
                    return float(sign * numpy.linalg.norm(a))

        @augment_class
        class Moving_Dynamical_Object(owlready2.Thing):
            @augment(AugmentationType.OBJECT_PROPERTY, "has_intersecting_path")
            def augment_has_intersecting_path(self, other: physics.Moving_Dynamical_Object):
                # TODO document in OWL (one entity needs 10s or less to predicted intersection point @ const. v)
                if same_scene(self, other) and has_geometry(self) and has_geometry(other) and self.has_yaw is not None \
                        and other.has_yaw is not None and self.has_speed is not None and other.has_speed is not None:
                    p_1 = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                    p_2 = wkt.loads(other.hasGeometry[0].asWKT[0]).centroid
                    p_self = geometry.Point(p_1.x, p_1.y)
                    p_other = geometry.Point(p_2.x, p_2.y)
                    if p_self != p_other:
                        self_path = geometry.Ray(p_self, angle=math.radians(self.has_yaw))
                        other_path = geometry.Ray(p_other, angle=math.radians(other.has_yaw))
                        p_cross = geometry.intersection(self_path, other_path)
                        if len(p_cross) > 0:
                            d_self = geometry.Point.distance(p_cross[0], p_self)
                            d_other = geometry.Point.distance(p_cross[0], p_other)
                            t_self = float(d_self) / self.has_speed
                            t_other = float(d_other) / other.has_speed
                            return t_self < _INTERSECTING_PATH_THRESHOLD or t_other < _INTERSECTING_PATH_THRESHOLD
                        else:
                            return False

            @augment(AugmentationType.OBJECT_PROPERTY, "CP_150")
            def augment_cp_150(self, other: physics.Moving_Dynamical_Object):
                # Small distance
                if self != other and same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    # TODO document in OWL
                    p_self = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                    p_other = wkt.loads(other.hasGeometry[0].asWKT[0]).centroid
                    # TODO find a better approximation than a simple circle here (use Kamm's circle?)
                    reachable_space = p_self.buffer(1.5 * self.has_speed)
                    return reachable_space.intersects(p_other)

            @augment(AugmentationType.OBJECT_PROPERTY, "CP_163")
            def augment_cp_163(self, other: physics.Moving_Dynamical_Object):
                # High relative speed
                if self != other and same_scene(self, other) and has_geometry(self) and has_geometry(other):
                    # TODO document in OWL (it is intentionally asymmetrical)
                    v_self = numpy.array([self.has_velocity_x, self.has_velocity_y])
                    v_other = numpy.array([other.has_velocity_x, other.has_velocity_y])
                    v_rel = v_self - v_other
                    s_rel = numpy.linalg.norm(v_rel)
                    s_rel_normed = s_rel / numpy.linalg.norm(v_other)
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
