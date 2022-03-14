import shapely.geometry

from owl_augmentator.owl_augmentator import augment, augment_class, AugmentationType
import owlready2
from .utils import *

import itertools
from shapely.geometry import Point, LineString
from shapely import wkt

_OCCLUSION_DISTANCE_THRESHOLD = 30


def register(physics: owlready2.Ontology, perception: owlready2.Ontology):
    with perception:

        @augment_class
        class Observer(owlready2.Thing):

            @augment(AugmentationType.REIFIED_OBJECT_PROPERTY, perception.Is_Full_Occlusion, ["is_occluded_for",
                                                                                              "is_occluded_by",
                                                                                              "is_occluded",
                                                                                              "in_traffic_model"])
            def augment_full_occlusion(self, occluding_object: physics.Spatial_Object,
                                       occluded_object: physics.Spatial_Object):
                occ = False
                # TODO: ! actually, we need to check "occluding_objects" (i.e., sets) here
                # TODO: consider yaw(?), visibility range and field of view of self
                # TODO: check if the assumption 'occluded object' shall have some height is justified
                # TODO: for sanity, at least reduce to a 50m radius or so...
                if same_scene(self, occluding_object) and same_scene(self, occluded_object) and \
                        self != occluding_object and occluding_object != occluded_object and \
                        self != occluded_object and has_geometry(self) and has_geometry(occluded_object) and \
                        has_geometry(occluding_object) and occluding_object.has_height and \
                        occluding_object.has_height > 0 and \
                        (len(self.drives) == 0 or (occluding_object not in self.drives)):
                    # TODO (see above) and self.has_visibility_range and self.has_horizontal_field_of_view:
                    p_other = wkt.loads(occluded_object.hasGeometry[0].asWKT[0])
                    if not isinstance(p_other, shapely.geometry.MultiPolygon) and \
                            not isinstance(p_other, shapely.geometry.point.Point):
                        # Right now we exclude points as occluded objects as a single point would not be visible anyhow
                        # TODO handle multipolygons (p.exterior.xy for p in Multi)
                        p_other_points = None
                        if hasattr(p_other, "exterior"):
                            p_other_points = p_other.exterior.coords
                        elif hasattr(p_other, "coords"):
                            p_other_points = p_other.coords
                        if p_other_points:
                            p_self = wkt.loads(self.hasGeometry[0].asWKT[0]).centroid
                            if len([p for p in p_other_points if p_self.distance(Point(p)) >
                                                                 _OCCLUSION_DISTANCE_THRESHOLD]) < len(p_other_points):
                                p_occluding = wkt.loads(occluding_object.hasGeometry[0].asWKT[0])
                                occ = True
                                for p in p_other_points:
                                    if not LineString([p_self, p]).intersects(p_occluding):
                                        occ = False
                                        break

                return occ, self.in_traffic_model[0]
